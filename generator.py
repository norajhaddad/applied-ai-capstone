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
    category: str = "linear"


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

# Acceleration due to gravity (m/s²), used by the free-fall category.
G = 9.81

# Which equations each category draws from. Free-fall fixes a = G, so it only
# uses equations that involve acceleration (the average-velocity one has no a).
_CATEGORY_EQUATIONS = {
    "linear": list(_EQUATIONS),
    "free-fall": [
        "final_velocity",
        "displacement",
        "displacement_from_final_velocity",
        "final_velocity_from_displacement",
    ],
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


def _format_prompt(
    given: dict[str, float], inputs: tuple[str, ...], target: str, category: str
) -> str:
    if category == "free-fall":
        # Acceleration is implied by g: state it in the prefix and leave it out
        # of the listed givens to avoid redundancy.
        shown = [name for name in inputs if name != "a"]
        givens = ", ".join(f"{name} = {given[name]} {_UNITS[name]}" for name in shown)
        return (
            f"Free fall (g = {G} m/s²): given {givens}, "
            f"find {_LABELS[target]} {target} ({_UNITS[target]})."
        )
    givens = ", ".join(f"{name} = {given[name]} {_UNITS[name]}" for name in inputs)
    return f"Given {givens}, find {_LABELS[target]} {target} ({_UNITS[target]})."


def generate(seed: int | None = None, category: str = "linear") -> Question:
    """Generate a reproducible SUVAT question.

    With a fixed ``seed`` the returned Question is identical on every call, and
    the answer is computed by the kinematics solver so it always matches.
    ``category`` selects the equation pool: "linear" (all five) or "free-fall"
    (acceleration fixed to G).
    """
    rng = random.Random(seed)
    equation = rng.choice(sorted(_CATEGORY_EQUATIONS[category]))
    target, inputs = _EQUATIONS[equation]
    given = {}
    for name in inputs:
        if name == "a" and category == "free-fall":
            given[name] = G
        else:
            given[name] = rng.randint(*_RANGES[name])
    answer = getattr(kinematics, equation)(**given)
    return Question(
        prompt=_format_prompt(given, inputs, target, category),
        given=given,
        target=target,
        unit=_UNITS[target],
        answer=answer,
        equation=equation,
        category=category,
    )


# Per-equation worked-solution templates: the formula with the given values
# substituted. Each references only variables present in that equation's
# `given`, plus {answer} and {unit}.
_WORKED = {
    "final_velocity": "v = u + a·t = {u} + {a}×{t} = {answer} {unit}",
    "displacement": "s = u·t + ½·a·t² = {u}×{t} + ½×{a}×{t}² = {answer} {unit}",
    "displacement_from_final_velocity": "s = v·t - ½·a·t² = {v}×{t} - ½×{a}×{t}² = {answer} {unit}",
    "final_velocity_from_displacement": "v = √(u² + 2·a·s) = √({u}² + 2×{a}×{s}) = {answer} {unit}",
    "displacement_from_velocities": "s = ½·(u + v)·t = ½×({u} + {v})×{t} = {answer} {unit}",
}


def _fmt(value: float) -> float | int:
    """Round to 2 dp and drop a trailing .0 so answers read cleanly."""
    rounded = round(float(value), 2)
    return int(rounded) if rounded == int(rounded) else rounded


def worked_solution(question: Question) -> str:
    """Render the equation for ``question`` with its given values substituted.

    e.g. "v = u + a·t = 0 + 5×4 = 20 m/s".
    """
    template = _WORKED[question.equation]
    return template.format(
        **question.given,
        answer=_fmt(question.answer),
        unit=question.unit,
    )
