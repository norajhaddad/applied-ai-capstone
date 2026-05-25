"""Tests for the SUVAT solver.

These are the spec — don't edit a test to force a pass. The scenario below
(u=0, a=9.8, t=2) gives v=19.6 and s=19.6, which every equation should agree on.
"""

import pytest

from kinematics import (
    displacement,
    displacement_from_final_velocity,
    displacement_from_velocities,
    final_velocity,
    final_velocity_from_displacement,
    projectile_max_height,
    projectile_range,
    projectile_time_of_flight,
)


# --- Textbook scenario: u=0, a=9.8, t=2  ->  v=19.6, s=19.6 ---

def test_final_velocity_textbook():
    # v = u + a*t = 0 + 9.8*2
    assert final_velocity(0, 9.8, 2) == pytest.approx(19.6)


def test_displacement_textbook():
    # s = u*t + 0.5*a*t^2 = 0 + 0.5*9.8*4
    assert displacement(0, 9.8, 2) == pytest.approx(19.6)


def test_displacement_from_final_velocity_textbook():
    # s = v*t - 0.5*a*t^2 = 19.6*2 - 0.5*9.8*4
    assert displacement_from_final_velocity(19.6, 9.8, 2) == pytest.approx(19.6)


def test_final_velocity_from_displacement_textbook():
    # v = sqrt(u^2 + 2*a*s) = sqrt(0 + 2*9.8*19.6)
    assert final_velocity_from_displacement(0, 9.8, 19.6) == pytest.approx(19.6)


def test_displacement_from_velocities_textbook():
    # s = 0.5*(u+v)*t = 0.5*(0+19.6)*2
    assert displacement_from_velocities(0, 19.6, 2) == pytest.approx(19.6)


# --- Edge: negative sqrt domain raises ValueError ---

def test_final_velocity_from_displacement_negative_domain():
    # u^2 + 2*a*s = 0 + 2*(-9.8)*10 = -196 < 0  ->  no real solution
    with pytest.raises(ValueError):
        final_velocity_from_displacement(0, -9.8, 10)


# --- Edge: a = 0 reduces to constant-velocity motion (no crash) ---

def test_zero_acceleration_is_constant_velocity():
    assert final_velocity(5, 0, 3) == 5
    assert displacement(5, 0, 3) == 15
    assert final_velocity_from_displacement(5, 0, 10) == 5  # sqrt(25)


# --- Projectile motion (launch from and landing at the same height) ---

def test_45_degrees_maximizes_range():
    u = 20
    r45 = projectile_range(u, 45)
    assert r45 >= projectile_range(u, 30)
    assert r45 >= projectile_range(u, 60)


def test_complementary_angles_give_equal_range():
    assert projectile_range(20, 30) == pytest.approx(projectile_range(20, 60))


def test_projectile_known_values_u10_45deg():
    # u=10 m/s, 45°, g=9.81: R=100/9.81, T=2u·sin45/g, H=(u·sin45)^2/(2g)
    assert projectile_range(10, 45) == pytest.approx(10.19, abs=0.01)
    assert projectile_time_of_flight(10, 45) == pytest.approx(1.4416, abs=0.001)
    assert projectile_max_height(10, 45) == pytest.approx(2.548, abs=0.01)


def test_straight_up_has_zero_range():
    assert projectile_range(15, 90) == pytest.approx(0, abs=1e-6)
