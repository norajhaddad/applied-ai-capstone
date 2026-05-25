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

## Task 3 — Question generator
- Brief: Add a seedable generator that picks 3 known SUVAT values + a target and uses the solver to compute the correct answer, returning a question object. Verify: with a fixed seed, generate() returns a reproducible question whose answer matches the solver.
- What Claude proposed: generator.py with generate(seed) using a local random.Random instance; a frozen Question dataclass (prompt, given, target, unit, answer, equation); five templates mapping each kinematics solver to its target + 3 input variables; integer sampling ranges kept non-negative so the √ equation never errors; answer computed via the solver. Plus tests/test_generator.py for reproducibility, variety, answer-matches-solver, and shape.
- What I changed before approving: Asked for nicer unit display — acceleration shows the superscript glyph (m/s²) in prompts instead of m/s^2 — and had a test added to pin that.
- Verification: .venv/bin/pytest -v → 12 passed (5 new). generate(seed=42) is reproducible; across 20 seeds, re-running the recorded equation on the givens matches the stored answer; a hand-check (seed 1: v=18, a=2, t=5 → s=65 m via displacement_from_final_velocity) agrees.
- One thing I learned: Seeding a local random.Random(seed) instead of the module-level random keeps the generator pure and reproducible without touching global state — same seed gives an identical question, and unrelated code can't perturb it. And recording which equation produced each answer (the `equation` field) is what lets a test independently re-derive the answer, turning "trust me" into "check me."

## Task 4 — Answer checker
- Brief: Add a function that parses the user's text to a float and compares it to the correct answer within a tolerance, flagging unparseable input. Verify: "19.6"→correct, a near-miss within tolerance passes, a far value fails, "abc"/""→flagged invalid (no crash).
- What Claude proposed: checker.py with a Result enum (CORRECT/INCORRECT/INVALID), parse_float(text)→float|None (strips whitespace; returns None on empty/garbage/non-finite, never raises), and check_answer(text, correct, rel_tol=0.01, abs_tol=...) built on math.isclose. Plus tests/test_checker.py covering correct, near-miss, far, invalid, whitespace, and near-zero.
- What I changed before approving: Bumped the absolute tolerance floor from 1e-6 to 0.05, so one-decimal rounding of small answers still counts while the 1% relative band keeps governing large answers. Deferred unit-stripping (accepting "19.6 m/s").
- Verification: .venv/bin/pytest -q → 25 passed (13 new). "19.6"→CORRECT; "19.5" (~0.5%)→CORRECT; "25"→INCORRECT; "abc"/""/"   "/"1.2.3"→INVALID with no exception; "inf"/"nan"→INVALID; near-zero handled by the floor.
- One thing I learned: math.isclose accepts a value within max(rel_tol·|value|, abs_tol), so setting both gives a "within 1% OR within 0.05" rule for free — the relative term handles big answers, the absolute floor rescues small/near-zero ones where a percentage is unfairly tight. And returning an INVALID result instead of letting float() raise keeps bad input a normal, testable outcome rather than a crash the web layer has to defend against.
