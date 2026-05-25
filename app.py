"""Flask application factory for the kinematics quiz.

Keeps the web layer thin: routes render templates and call the pure
generator/checker modules. Quiz state will live in the Flask session, so a
SECRET_KEY is configured here even though sessions arrive in a later task.
"""

from __future__ import annotations

import os

from flask import Flask, render_template


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

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
