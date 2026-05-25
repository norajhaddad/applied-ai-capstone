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

# Projectile launch problems (level ground, g implied). Givens are launch speed
# u and launch angle; the target is one of range / max height / time of flight.
_PROJECTILE = {
    "projectile_range": ("range", "m"),
    "projectile_max_height": ("max height", "m"),
    "projectile_time_of_flight": ("time of flight", "s"),
}

_PROJECTILE_RANGES = {
    "u": (5, 40),           # launch speed, m/s
    "angle_deg": (15, 75),  # launch angle, degrees
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
    ``category`` selects the pool: "linear" (all five SUVAT equations),
    "free-fall" (acceleration fixed to G), "projectile" (launch problems), or
    "all" (a random mix of the three).
    """
    rng = random.Random(seed)
    if category == "all":
        # Mixed practice: resolve to a concrete category, recorded on the Question.
        category = rng.choice(["free-fall", "linear", "projectile"])
    if category == "projectile":
        return _generate_projectile(rng)
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


def _generate_projectile(rng: random.Random) -> Question:
    """Build a projectile question (launch speed + angle; g implied)."""
    equation = rng.choice(sorted(_PROJECTILE))
    label, unit = _PROJECTILE[equation]
    given = {
        "u": rng.randint(*_PROJECTILE_RANGES["u"]),
        "angle_deg": rng.randint(*_PROJECTILE_RANGES["angle_deg"]),
    }
    answer = getattr(kinematics, equation)(**given)
    prompt = (
        f"Projectile launched at u = {given['u']} m/s, "
        f"θ = {given['angle_deg']}° (g = {G} m/s²). Find the {label} ({unit})."
    )
    return Question(
        prompt=prompt,
        given=given,
        target=label,
        unit=unit,
        answer=answer,
        equation=equation,
        category="projectile",
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
    "projectile_range": "R = u²·sin(2θ)/g = {u}²·sin(2×{angle_deg}°)/{g} = {answer} {unit}",
    "projectile_max_height": "H = (u·sinθ)²/(2g) = ({u}·sin{angle_deg}°)²/(2×{g}) = {answer} {unit}",
    "projectile_time_of_flight": "T = 2·u·sinθ/g = 2×{u}×sin{angle_deg}°/{g} = {answer} {unit}",
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
        g=G,
    )
