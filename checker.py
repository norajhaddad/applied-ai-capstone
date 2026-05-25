"""Answer checker for the kinematics quiz.

Parses a user's typed answer to a float and judges it against the correct value
within a tolerance. Pure: no Flask, no I/O, no global state.
"""

from __future__ import annotations

import math
from enum import Enum


class Result(Enum):
    """Outcome of checking a typed answer."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    INVALID = "invalid"  # could not parse a finite number


def parse_float(text: str) -> float | None:
    """Parse user input to a finite float, or None if it isn't one.

    Strips surrounding whitespace. Empty strings, non-numeric text, and
    non-finite values (inf, nan) all return None rather than raising.
    """
    try:
        value = float(text.strip())
    except (ValueError, AttributeError):
        return None
    if not math.isfinite(value):
        return None
    return value


def check_answer(
    text: str,
    correct: float,
    *,
    rel_tol: float = 0.01,
    abs_tol: float = 0.05,
) -> Result:
    """Check a typed answer against the correct value.

    Accepts the answer when it is within ``rel_tol`` (relative) OR ``abs_tol``
    (absolute) of ``correct`` — whichever band is larger, per math.isclose. The
    0.05 absolute floor means a one-decimal rounding of a small answer still
    counts. Unparseable or non-finite input returns Result.INVALID (never raises).
    """
    value = parse_float(text)
    if value is None:
        return Result.INVALID
    if math.isclose(value, correct, rel_tol=rel_tol, abs_tol=abs_tol):
        return Result.CORRECT
    return Result.INCORRECT
