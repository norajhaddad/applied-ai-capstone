"""Constant-acceleration (SUVAT) kinematics solver.

Pure functions implementing the five standard equations of motion for constant
acceleration. Variables follow the usual SUVAT naming:

    s  displacement
    u  initial velocity
    v  final velocity
    a  acceleration
    t  time

No Flask, no I/O, no global state — just math, so this stays trivially
unit-testable.
"""

from __future__ import annotations

import math


def final_velocity(u: float, a: float, t: float) -> float:
    """Final velocity, given initial velocity, acceleration, and time.

    v = u + a * t

    With a = 0 this reduces to constant velocity (v = u).
    """
    return u + a * t


def displacement(u: float, a: float, t: float) -> float:
    """Displacement, given initial velocity, acceleration, and time.

    s = u * t + 0.5 * a * t**2

    With a = 0 this reduces to constant-velocity motion (s = u * t).
    """
    return u * t + 0.5 * a * t**2


def displacement_from_final_velocity(v: float, a: float, t: float) -> float:
    """Displacement, given final velocity, acceleration, and time.

    s = v * t - 0.5 * a * t**2
    """
    return v * t - 0.5 * a * t**2


def final_velocity_from_displacement(u: float, a: float, s: float) -> float:
    """Final velocity, given initial velocity, acceleration, and displacement.

    v = sqrt(u**2 + 2 * a * s)

    Returns the non-negative root by convention.

    Raises:
        ValueError: if u**2 + 2 * a * s < 0, i.e. there is no real solution
            (the motion never reaches that displacement).
    """
    radicand = u**2 + 2 * a * s
    if radicand < 0:
        raise ValueError(
            f"no real final velocity: u**2 + 2*a*s = {radicand} is negative"
        )
    return math.sqrt(radicand)


def displacement_from_velocities(u: float, v: float, t: float) -> float:
    """Displacement, given initial velocity, final velocity, and time.

    s = 0.5 * (u + v) * t   (distance as average velocity times time)
    """
    return 0.5 * (u + v) * t


def projectile_time_of_flight(u: float, angle_deg: float, g: float = 9.81) -> float:
    """Time of flight for a projectile launched from and landing at the same height.

    T = 2 * u * sin(θ) / g, with θ = ``angle_deg`` in degrees.
    """
    return 2 * u * math.sin(math.radians(angle_deg)) / g


def projectile_max_height(u: float, angle_deg: float, g: float = 9.81) -> float:
    """Maximum height reached by a projectile launched at ``angle_deg`` with speed u.

    H = (u * sin(θ))**2 / (2 * g)
    """
    uy = u * math.sin(math.radians(angle_deg))
    return uy**2 / (2 * g)


def projectile_range(u: float, angle_deg: float, g: float = 9.81) -> float:
    """Horizontal range of a projectile over level ground.

    R = u**2 * sin(2θ) / g, with θ = ``angle_deg`` in degrees. Maximised at 45°.
    """
    return u**2 * math.sin(math.radians(2 * angle_deg)) / g
