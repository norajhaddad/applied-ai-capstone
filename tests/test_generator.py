"""Tests for the SUVAT question generator. These are the spec."""

import pytest

import kinematics
from generator import Question, generate


def test_reproducible_with_seed():
    # Same seed -> identical question, every time.
    assert generate(seed=42) == generate(seed=42)


def test_seeds_produce_variety():
    questions = [generate(seed=s) for s in range(10)]
    assert any(q != questions[0] for q in questions[1:])


def test_answer_matches_solver():
    # The stored answer must equal a fresh run of the recorded equation.
    for seed in range(20):
        q = generate(seed=seed)
        recomputed = getattr(kinematics, q.equation)(**q.given)
        assert recomputed == pytest.approx(q.answer)


def test_question_shape():
    q = generate(seed=7)
    assert isinstance(q, Question)
    assert len(q.given) == 3          # exactly three knowns
    assert q.target not in q.given    # we always solve for the unknown
    assert q.target in q.prompt
    assert q.unit


def test_acceleration_uses_superscript_unit():
    # The chosen tweak: acceleration is shown as m/s² (superscript), not m/s^2.
    for seed in range(50):
        q = generate(seed=seed)
        if "a" in q.given:
            assert "m/s²" in q.prompt
            return
    pytest.fail("no acceleration question generated in 50 seeds")
