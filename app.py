"""Flask application factory for the kinematics quiz.

Keeps the web layer thin: routes render templates and delegate to the pure
generator/checker modules. Quiz state (current question, score, chosen
category) lives in the Flask session. Errors are handled gracefully — see the
handlers in create_app — so a user never sees a raw traceback.
"""

from __future__ import annotations

import os
from dataclasses import asdict

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.exceptions import HTTPException

import generator
from checker import Result, check_answer
from generator import Question

# Category filter options for the quiz selector (key, display label).
CATEGORIES = [("all", "All"), ("linear", "Linear"), ("free-fall", "Free-fall"), ("projectile", "Projectile")]
_VALID_CATEGORIES = {key for key, _ in CATEGORIES}

# Placeholder secret, acceptable only for local dev/testing. Any other context
# must supply a real SECRET_KEY via the environment (enforced in create_app).
_DEV_SECRET = "dev-secret-change-me"

# Longest answer string we'll parse — guards against pathological input.
_MAX_ANSWER_LEN = 64


def create_app(test_config: dict | None = None) -> Flask:
    """Build and configure the Flask app.

    Args:
        test_config: optional config overrides, merged in after the defaults
            (used by tests to flip on TESTING, inject a fixed key, etc.).
    """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", _DEV_SECRET),
    )
    if test_config is not None:
        app.config.update(test_config)

    # Fail fast rather than run insecurely: the placeholder key is only allowed
    # in debug or testing. Anywhere else, demand a real SECRET_KEY.
    if app.config["SECRET_KEY"] == _DEV_SECRET and not (app.debug or app.config.get("TESTING")):
        raise RuntimeError(
            "Refusing to start with the insecure default SECRET_KEY. Set the "
            "SECRET_KEY environment variable (or run in debug/testing)."
        )

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/quiz", methods=["GET", "POST"])
    def quiz():
        if request.method == "POST":
            stored = session.get("question")
            if stored is None:
                # No question to grade (fresh/expired session) — start over.
                return redirect(url_for("quiz"))
            try:
                question = Question(**stored)
            except (TypeError, ValueError):
                # Stale or garbled session payload — start fresh, don't 500.
                session.pop("question", None)
                return redirect(url_for("quiz"))
            typed = request.form.get("answer", "")[:_MAX_ANSWER_LEN]
            result = check_answer(typed, question.answer)
            category = session.get("category", "all")
            if result is Result.INVALID:
                # Re-render the same question with an error, keeping the input.
                return render_template(
                    "quiz.html",
                    question=question,
                    typed=typed,
                    error="Please enter a number.",
                    category=category,
                    categories=CATEGORIES,
                )
            # Only graded answers count toward the score (invalid input above
            # returns before this point).
            session["attempts"] = session.get("attempts", 0) + 1
            if result is Result.CORRECT:
                session["correct"] = session.get("correct", 0) + 1
            return render_template(
                "result.html",
                question=question,
                typed=typed,
                correct=(result is Result.CORRECT),
                worked=generator.worked_solution(question),
                category=category,
            )
        # GET: fresh question in the selected category, stashed for the POST.
        category = request.args.get("category", "all")
        if category not in _VALID_CATEGORIES:
            category = "all"
        session["category"] = category
        question = generator.generate(category=category)
        session["question"] = asdict(question)
        return render_template(
            "quiz.html", question=question, category=category, categories=CATEGORIES
        )

    @app.route("/reset", methods=["POST"])
    def reset():
        session.pop("attempts", None)
        session.pop("correct", None)
        return redirect(url_for("quiz"))

    @app.route("/healthz")
    def healthz():
        # Lightweight liveness check for uptime monitors / load balancers.
        return jsonify(status="ok"), 200

    def _error_page(code: int, message: str):
        return render_template("error.html", code=code, message=message), code

    @app.errorhandler(404)
    def _not_found(_error):
        return _error_page(404, "We couldn't find that page.")

    @app.errorhandler(405)
    def _method_not_allowed(_error):
        return _error_page(405, "That action isn't allowed here.")

    @app.errorhandler(HTTPException)
    def _http_error(error):
        # Any other HTTP error (e.g. 400): friendly page, original status code.
        return _error_page(error.code or 500, error.description or "Request error.")

    @app.errorhandler(Exception)
    def _unexpected(_error):
        # Last line of defence: log the real cause, show the user a calm message.
        app.logger.exception("Unhandled exception")
        return _error_page(500, "Something went wrong on our end.")

    return app


if __name__ == "__main__":
    # Local development server only — not for production. For production, set a
    # real SECRET_KEY and serve create_app() with a WSGI server (e.g. gunicorn).
    create_app({"DEBUG": True}).run(debug=True, port=5000)
