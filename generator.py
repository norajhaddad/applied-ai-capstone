"""Seedable generator for constant-acceleration (SUVAT) practice questions.

Picks one of the five SUVAT equations, samples three input values, and uses the
kinematics solver to compute the correct answer. Pure and seedable: the same
seed always produces the same Question, and there is no global state.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import kinematics


@dataclass(frozen=True)
class Question:
    """A single practice question and its solver-computed answer."""

    prompt: str
    given: dict[str, float]
    target: str
    unit: str
    answer: float
    equation: str


# Display units per SUVAT variable. Acceleration uses the superscript-² glyph.
_UNITS = {
    "s": "m",
    "u": "m/s",
    "v": "m/s",
    "a": "m/s²",
    "t": "s",
}

# Human-readable name for the quantity being solved for.
_LABELS = {
    "s": "displacement",
    "u": "initial velocity",
    "v": "final velocity",
    "a": "acceleration",
    "t": "time",
}

# equation/solver name -> (target variable, ordered input variables). The key is
# the kinematics function name, so the answer can be recomputed independently
# with getattr(kinematics, equation)(**given).
_EQUATIONS = {
    "final_velocity": ("v", ("u", "a", "t")),
    "displacement": ("s", ("u", "a", "t")),
    "displacement_from_final_velocity": ("s", ("v", "a", "t")),
    "final_velocity_from_displacement": ("v", ("u", "a", "s")),
    "displacement_from_velocities": ("s", ("u", "v", "t")),
}

# Inclusive integer sampling ranges, kept non-negative so √(u² + 2as) always has
# a real solution (no spurious ValueError from the solver).
_RANGES = {
    "s": (1, 100),
    "u": (0, 30),
    "v": (0, 30),
    "a": (1, 10),
    "t": (1, 10),
}


def _format_prompt(given: dict[str, float], inputs: tuple[str, ...], target: str) -> str:
    givens = ", ".join(f"{name} = {given[name]} {_UNITS[name]}" for name in inputs)
    return f"Given {givens}, find {_LABELS[target]} {target} ({_UNITS[target]})."


def generate(seed: int | None = None) -> Question:
    """Generate a reproducible SUVAT question.

    With a fixed ``seed`` the returned Question is identical on every call. The
    answer is computed by the kinematics solver, so it always matches the solver.
    """
    rng = random.Random(seed)
    equation = rng.choice(sorted(_EQUATIONS))
    target, inputs = _EQUATIONS[equation]
    given = {name: rng.randint(*_RANGES[name]) for name in inputs}
    answer = getattr(kinematics, equation)(**given)
    return Question(
        prompt=_format_prompt(given, inputs, target),
        given=given,
        target=target,
        unit=_UNITS[target],
        answer=answer,
        equation=equation,
    )
