# Kinematics Practice Quiz

A small Flask web app that generates randomized constant-acceleration (SUVAT)
problems, checks your numeric answer within a tolerance, shows the worked
solution, and tracks your score. Built as a capstone; intentionally small.

Two categories: **Linear** (general SUVAT) and **Free-fall** (a = g = 9.81 m/s²),
selectable in the UI or via the `?category=` query parameter.

## Requirements

- Python 3.10+

## Setup

```bash
git clone <repo-url>
cd applied-ai-capstone
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open http://localhost:5000 and start practicing.

## Test

```bash
pytest
```

## Project layout

- `kinematics.py` — pure SUVAT solver (the five equations of motion)
- `generator.py` — seedable question generator + worked-solution formatter
- `checker.py` — tolerance-based answer checker
- `app.py` — Flask app factory and routes (home, /quiz, /reset)
- `templates/`, `static/` — Jinja templates and CSS
- `tests/` — pytest suite
- `BUILD_LOG.md` — a short per-task record of how this was built

## Notes

- The Flask development server (`python app.py`) is for local use only. In
  production, set a real `SECRET_KEY` environment variable and serve
  `create_app()` with a WSGI server (e.g. gunicorn) — the app refuses to start
  with the insecure default key outside debug/testing.
- `GET /healthz` returns `{"status": "ok"}` for uptime checks.
- Invalid input, unknown URLs, and unexpected errors all render a friendly page
  rather than a stack trace.
