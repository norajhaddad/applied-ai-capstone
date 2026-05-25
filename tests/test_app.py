"""Tests for the Flask web shell."""

import pytest

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
    # Pin the category so the prompt deterministically reads "Given ..., find ...".
    data = _client().get("/quiz?category=linear").data
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


def _start_quiz(client):
    client.get("/quiz")
    with client.session_transaction() as sess:
        return sess["question"]


def test_correct_answer_shows_correct():
    client = _client()
    q = _start_quiz(client)
    resp = client.post("/quiz", data={"answer": str(q["answer"])})
    assert resp.status_code == 200
    assert b"Correct!" in resp.data


def test_wrong_answer_shows_incorrect():
    client = _client()
    q = _start_quiz(client)
    resp = client.post("/quiz", data={"answer": str(q["answer"] + 1000)})
    assert b"Incorrect" in resp.data


def test_empty_input_rerenders_with_error():
    client = _client()
    _start_quiz(client)
    resp = client.post("/quiz", data={"answer": ""})
    assert resp.status_code == 200
    assert b"Please enter a number" in resp.data
    assert b'name="answer"' in resp.data  # the form is still there


def test_garbage_input_keeps_typed_value():
    client = _client()
    _start_quiz(client)
    resp = client.post("/quiz", data={"answer": "abc"})
    assert b"Please enter a number" in resp.data
    assert b'value="abc"' in resp.data  # the typed value is preserved


def test_result_shows_worked_solution():
    client = _client()
    q = _start_quiz(client)
    resp = client.post("/quiz", data={"answer": str(q["answer"])})
    assert b"=" in resp.data  # the worked equation is rendered


def test_score_tracks_attempts_and_correct():
    client = _client()
    for _ in range(2):  # two correct
        q = _start_quiz(client)
        client.post("/quiz", data={"answer": str(q["answer"])})
    q = _start_quiz(client)  # one wrong
    client.post("/quiz", data={"answer": str(q["answer"] + 1000)})
    with client.session_transaction() as sess:
        assert sess["correct"] == 2
        assert sess["attempts"] == 3
    assert b"2 / 3" in client.get("/quiz").data


def test_invalid_submission_does_not_count():
    client = _client()
    _start_quiz(client)
    client.post("/quiz", data={"answer": "abc"})
    with client.session_transaction() as sess:
        assert sess.get("attempts", 0) == 0


def test_reset_zeroes_the_score():
    client = _client()
    q = _start_quiz(client)
    client.post("/quiz", data={"answer": str(q["answer"])})
    client.post("/reset")
    with client.session_transaction() as sess:
        assert sess.get("attempts", 0) == 0
        assert sess.get("correct", 0) == 0
    assert b"0 / 0" in client.get("/").data


def _quiz_category(client, query=""):
    client.get("/quiz" + query)
    with client.session_transaction() as sess:
        return sess["question"]["category"]


def test_linear_filter_serves_only_linear():
    client = _client()
    for _ in range(10):
        assert _quiz_category(client, "?category=linear") == "linear"


def test_free_fall_filter_serves_only_free_fall():
    client = _client()
    for _ in range(10):
        assert _quiz_category(client, "?category=free-fall") == "free-fall"


def test_all_filter_mixes_categories():
    client = _client()
    seen = {_quiz_category(client, "?category=all") for _ in range(40)}
    assert "linear" in seen and "free-fall" in seen


def test_quiz_shows_category_selector():
    data = _client().get("/quiz").data
    assert b"category=linear" in data
    assert b"category=free-fall" in data


def test_unknown_category_does_not_crash():
    assert _client().get("/quiz?category=bogus").status_code == 200


def test_home_shows_score_summary():
    assert b"No questions answered yet" in _client().get("/").data


def test_static_css_is_served():
    assert _client().get("/static/style.css").status_code == 200


def test_pages_use_semantic_landmarks():
    data = _client().get("/").data
    assert b"<main" in data and b"<header" in data and b"<footer" in data


def test_answer_input_has_associated_label():
    data = _client().get("/quiz?category=linear").data
    assert b'for="answer"' in data and b'id="answer"' in data


def test_verdict_is_an_aria_live_status():
    client = _client()
    q = _start_quiz(client)
    data = client.post("/quiz", data={"answer": str(q["answer"])}).data
    assert b'role="status"' in data


def test_projectile_filter_serves_only_projectile():
    client = _client()
    for _ in range(10):
        assert _quiz_category(client, "?category=projectile") == "projectile"


def test_selector_includes_projectile():
    assert b"category=projectile" in _client().get("/quiz").data


# --- Hardening: graceful errors, health check, defensive guards, config ---

def test_unknown_url_returns_friendly_404():
    resp = _client().get("/no-such-page")
    assert resp.status_code == 404
    assert b"Error 404" in resp.data


def test_wrong_method_returns_405():
    resp = _client().get("/reset")  # reset is POST-only
    assert resp.status_code == 405
    assert b"Error 405" in resp.data


def test_healthz_returns_ok_json():
    resp = _client().get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_unexpected_error_shows_friendly_500(monkeypatch):
    import generator

    def _boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(generator, "generate", _boom)
    app = create_app({"TESTING": True, "PROPAGATE_EXCEPTIONS": False})
    resp = app.test_client().get("/quiz")
    assert resp.status_code == 500
    assert b"went wrong" in resp.data


def test_malformed_session_does_not_crash():
    client = _client()
    with client.session_transaction() as sess:
        sess["question"] = {"bogus": "data"}  # not a valid Question payload
    resp = client.post("/quiz", data={"answer": "5"})
    assert resp.status_code in (302, 303)  # redirected to a fresh quiz, not 500


def test_overlong_answer_is_handled():
    client = _client()
    _start_quiz(client)
    resp = client.post("/quiz", data={"answer": "9" * 5000})
    assert resp.status_code == 200  # capped + treated as a normal (wrong) answer


def test_refuses_insecure_secret_key_outside_debug(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        create_app()  # no TESTING, no DEBUG, default key -> refuse to start


def test_accepts_real_secret_key(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a-real-secret")
    app = create_app()  # real key -> allowed even without debug/testing
    assert app.config["SECRET_KEY"] == "a-real-secret"
