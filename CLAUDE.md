# Kinematics Practice Quiz

A small Flask web app that generates randomized constant-acceleration (SUVAT)
problems, checks numeric answers within a tolerance, and tracks score. Built as
a capstone; kept intentionally small.

## Stack

- Python 3.10+
- Flask (with Jinja2 templates)
- vanilla HTML/CSS
- pytest for tests
- No database — state lives in-memory / the Flask session

## How to run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                    # serves http://localhost:5000
pytest                           # run the tests
```

## Conventions

- Plan before coding.
- Tests are the spec — don't edit a test to force a pass.
- Work on feature branches; never commit straight to `main`.
- Keep the pure logic (solver, generator, answer checker) free of Flask, I/O,
  and global state so it stays unit-testable.

## Architecture

This will grow over later tasks. Planned pieces:

- `kinematics.py` — the pure SUVAT solver (start here).
- problem generator, answer checker — pure logic, added next.
- app factory, templates — the Flask layer.
- tests — alongside the above.
