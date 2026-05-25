# Build Log

A short entry per task: the brief, what Claude proposed, what I changed before
approving, how I verified it, and one thing I learned. The point is to capture
the decisions as they happen — code is cheap, the reasoning is the artifact.

## Task 1 — Scaffold + CLAUDE.md
- Brief: Create CLAUDE.md, .gitignore, requirements.txt (pytest), and pyproject.toml with `pythonpath = ["."]`. Verify a fresh session loads CLAUDE.md and `pytest` runs from the repo root collecting 0 tests with no import errors.
- What Claude proposed: CLAUDE.md + .gitignore were already committed earlier; add `requirements.txt` (pytest only — Flask comes in Task 5), `pyproject.toml` with `[tool.pytest.ini_options]` setting `pythonpath = ["."]` and `testpaths = ["tests"]`, a `tests/` dir so testpaths resolves, and start this BUILD_LOG.
- What I changed before approving: Approved the file plan as proposed; separately chose GitHub PR-per-task as the merge flow for the whole build.
- Verification: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/pytest` from the repo root → config loaded from pyproject.toml, `testpaths: tests` resolved, "collected 0 items / no tests ran", no import errors. (pytest exits code 5 = "no tests collected" — expected for an empty suite.)
- One thing I learned: pytest returns exit code 5 when it collects zero tests — that means "nothing to run," not "something broke," so an empty scaffold is healthy rather than failing. `pythonpath = ["."]` in pyproject.toml is what lets tests import top-level modules without packaging or installing the project.

## Task 2 — SUVAT solver
- Brief: Add kinematics.py with the five named, documented constant-acceleration functions. Verify pytest passes textbook cases (u=0, a=9.8, t=2 → v=19.6, s≈19.6) and edge cases (ValueError on negative sqrt domain, a=0).
- What Claude proposed: Five pure, type-hinted, documented functions with no Flask/I/O/globals — final_velocity (v=u+at), displacement (s=ut+½at²), displacement_from_final_velocity (s=vt−½at²), final_velocity_from_displacement (v=√(u²+2as)), displacement_from_velocities (s=½(u+v)t). The sqrt function raises ValueError on a negative radicand and returns the non-negative root; a=0 is left to reduce naturally to constant velocity. Plus tests/test_kinematics.py covering all of it.
- What I changed before approving: Approved as proposed.
- Verification: .venv/bin/pytest -v → 7 passed. The textbook scenario (u=0, a=9.8, t=2) was cross-checked across all five equations (each gives v=19.6 / s=19.6); the negative-domain case raises ValueError; a=0 returns constant-velocity values (v=u, s=u·t).
- One thing I learned: The five SUVAT equations are all rearrangements of the same motion, so a single scenario can cross-check every function — they must all agree on v=19.6 and s=19.6, which makes a tiny test suite surprisingly thorough. Only the v=√(...) form can fail on real inputs (negative radicand), which is why it's the one function that needs an explicit guard.
