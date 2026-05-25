"""Tests for the answer checker. These are the spec."""

import pytest

from checker import Result, check_answer, parse_float


def test_exact_correct():
    assert check_answer("19.6", 19.6) is Result.CORRECT


def test_near_miss_within_tolerance_passes():
    # 19.5 vs 19.6 is ~0.5%, inside the 1% relative band.
    assert check_answer("19.5", 19.6) is Result.CORRECT


def test_far_value_is_incorrect():
    assert check_answer("25", 19.6) is Result.INCORRECT


@pytest.mark.parametrize("text", ["abc", "", "   ", "1.2.3", "twelve"])
def test_unparseable_is_invalid_and_does_not_crash(text):
    assert check_answer(text, 19.6) is Result.INVALID


def test_surrounding_whitespace_ok():
    assert check_answer("  19.6  ", 19.6) is Result.CORRECT


def test_absolute_floor_helps_small_answers():
    # 1% of ~2 is only ~0.02; the 0.05 floor lets a one-decimal answer pass.
    assert check_answer("2.0", 2.04) is Result.CORRECT    # diff 0.04 < 0.05
    assert check_answer("2.2", 2.04) is Result.INCORRECT  # diff 0.16 > 0.05


def test_near_zero_answer():
    assert check_answer("0", 0.0) is Result.CORRECT
    assert check_answer("0.03", 0.0) is Result.CORRECT    # within abs_tol
    assert check_answer("0.5", 0.0) is Result.INCORRECT


def test_non_finite_is_invalid():
    assert check_answer("inf", 19.6) is Result.INVALID
    assert check_answer("nan", 19.6) is Result.INVALID


def test_parse_float_helper():
    assert parse_float(" 3.5 ") == 3.5
    assert parse_float("abc") is None
    assert parse_float("") is None
