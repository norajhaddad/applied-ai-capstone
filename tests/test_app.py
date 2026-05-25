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


def test_quiz_route_returns_200():
    assert _client().get("/quiz").status_code == 200


def test_quiz_page_has_prompt_and_answer_field():
    data = _client().get("/quiz").data
    # Every generated prompt reads "Given ..., find ...".
    assert b"Given" in data and b"find" in data
    assert b'name="answer"' in data


def test_quiz_stores_question_in_session():
    client = _client()
    client.get("/quiz")
    with client.session_transaction() as sess:
        assert "question" in sess
        assert "answer" in sess["question"]  # answer kept server-side for checking


def test_home_links_to_quiz():
    assert b"/quiz" in _client().get("/").data
