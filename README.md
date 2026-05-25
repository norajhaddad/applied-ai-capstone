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
