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
