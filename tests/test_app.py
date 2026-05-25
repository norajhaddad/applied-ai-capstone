"""Tests for the Flask web shell."""

from app import create_app


def _client():
    return create_app({"TESTING": True}).test_client()


def test_home_route_returns_200():
    assert _client().get("/").status_code == 200


def test_home_page_renders_title():
    assert b"Kinematics Practice Quiz" in _client().get("/").data


def test_app_factory_accepts_test_config():
    app = create_app({"TESTING": True})
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"]  # a default key is always configured
