"""Flask application factory for the kinematics quiz.

Keeps the web layer thin: routes render templates and call the pure
generator/checker modules. Quiz state will live in the Flask session, so a
SECRET_KEY is configured here even though sessions arrive in a later task.
"""

from __future__ import annotations

import os
from dataclasses import asdict

from flask import Flask, redirect, render_template, request, session, url_for

import generator
from checker import Result, check_answer
from generator import Question


def create_app(test_config: dict | None = None) -> Flask:
    """Build and configure the Flask app.

    Args:
        test_config: optional config overrides, merged in after the defaults
            (used by tests to flip on TESTING, inject a fixed key, etc.).
    """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
    )
    if test_config is not None:
        app.config.update(test_config)

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
            question = Question(**stored)
            typed = request.form.get("answer", "")
            result = check_answer(typed, question.answer)
            if result is Result.INVALID:
                # Re-render the same question with an error, keeping the input.
                return render_template(
                    "quiz.html",
                    question=question,
                    typed=typed,
                    error="Please enter a number.",
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
            )
        # GET: fresh question, stashed so the POST can check against it.
        question = generator.generate()
        session["question"] = asdict(question)
        return render_template("quiz.html", question=question)

    @app.route("/reset", methods=["POST"])
    def reset():
        session.pop("attempts", None)
        session.pop("correct", None)
        return redirect(url_for("quiz"))

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
