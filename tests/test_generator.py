"""Tests for the SUVAT question generator. These are the spec."""

import pytest

import kinematics
from generator import Question, generate, worked_solution


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


def _make(equation, given, unit):
    # Build a Question with the real solver answer, for worked-solution tests.
    answer = getattr(kinematics, equation)(**given)
    return Question(prompt="", given=given, target="", unit=unit, answer=answer,
                    equation=equation)


def test_worked_solution_final_velocity():
    q = _make("final_velocity", {"u": 0, "a": 5, "t": 4}, "m/s")
    assert worked_solution(q) == "v = u + a·t = 0 + 5×4 = 20 m/s"


def test_worked_solution_displacement():
    q = _make("displacement", {"u": 2, "a": 3, "t": 4}, "m")
    assert worked_solution(q) == "s = u·t + ½·a·t² = 2×4 + ½×3×4² = 32 m"


def test_worked_solution_displacement_from_final_velocity():
    q = _make("displacement_from_final_velocity", {"v": 10, "a": 2, "t": 3}, "m")
    assert worked_solution(q) == "s = v·t - ½·a·t² = 10×3 - ½×2×3² = 21 m"


def test_worked_solution_sqrt():
    q = _make("final_velocity_from_displacement", {"u": 0, "a": 8, "s": 9}, "m/s")
    assert worked_solution(q) == "v = √(u² + 2·a·s) = √(0² + 2×8×9) = 12 m/s"


def test_worked_solution_from_velocities():
    q = _make("displacement_from_velocities", {"u": 2, "v": 8, "t": 5}, "m")
    assert worked_solution(q) == "s = ½·(u + v)·t = ½×(2 + 8)×5 = 25 m"


def test_free_fall_uses_gravity_and_matches_solver():
    for seed in range(20):
        q = generate(seed=seed, category="free-fall")
        assert q.category == "free-fall"
        assert q.given["a"] == pytest.approx(9.81)
        assert getattr(kinematics, q.equation)(**q.given) == pytest.approx(q.answer)


def test_free_fall_excludes_no_acceleration_equation():
    equations = {generate(seed=s, category="free-fall").equation for s in range(50)}
    assert "displacement_from_velocities" not in equations
    assert equations  # sanity: some questions were generated


def test_free_fall_prompt_is_labeled():
    q = generate(seed=3, category="free-fall")
    assert "Free fall" in q.prompt
    assert "9.81" in q.prompt


def test_default_category_is_linear():
    assert generate(seed=1).category == "linear"
