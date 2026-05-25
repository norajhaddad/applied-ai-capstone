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
