# Trajectory

A personal health dashboard for understanding the relationship between daily behavior and metabolic outcomes. Trajectory pulls CGM readings, meals, goals, wearable-style daily metrics, lab trends, subjective check-ins, and weekly summaries into one calm, data-dense view.

It's designed to help a returning user answer three questions in under five seconds:

- Am I on track?
- What changed this week?
- What should I pay attention to next?

The product is single-participant and local-first. See [`design_doc.md`](design_doc.md) for the full product and technical spec.

## Stack

- **Frontend:** React 18 + Vite
- **Backend:** FastAPI (Python)
- **Database:** SQLite

## Surfaces

- **Overview** — the primary mission-control dashboard: composite score, goal rings, KPI grid (avg glucose, time in range, GMI, steps, sleep, HRV), daily glucose chart, post-meal response, correlations, and a daily check-in.
- **Coach** — a narrative weekly briefing over the same data layer.

## Project layout

```text
backend/
  main.py          FastAPI app and routes
  db.py            SQLite connection helpers
  models.py        Pydantic request/response models
  calculations.py  GMI, TIR, deltas, score, Pearson r
  queries.py       SQL query helpers
  seed.py          deterministic local dataset generation
  schema.sql       database schema
  tests/           backend tests
frontend/
  src/
    api.js         API client
    tokens.js      design tokens
    App.jsx
    components/    Overview, Coach, charts, primitives, ...
```

## Getting started

### 1. Backend

From the repo root, create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Seed the local database (deterministic). Use `--full` for 90 days at 5-minute CGM cadence, or `--fast` for a smaller dataset for tests/CI:

```bash
python backend/seed.py --full
```

Run the API (defaults to port 8000):

```bash
cd backend
uvicorn main:app --reload
```

### 2. Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite serves the app and proxies `/api` to the FastAPI backend at `http://localhost:8000`, so no CORS configuration is needed in development.

## API

The canonical Overview endpoint returns one consistent dashboard snapshot:

```http
GET /api/v1/dashboard?window=7d
```

Supported windows: `7d`, `14d`, `30d`, `90d`.

Additional endpoints:

```http
GET  /api/v1/kpis?window=7d
GET  /api/v1/glucose/series?window=14d
GET  /api/v1/correlations?window=30d
GET  /api/v1/checkin/today
POST /api/v1/checkin
GET  /api/briefing
GET  /api/goals
GET  /api/meals/response?name=Rice%20%26%20dal
GET  /api/labs?marker=eGFR
```

## Tests

Backend tests cover the derived-metric formulas (GMI, time in range, percent delta, composite score, Pearson correlation) and the dashboard/check-in API contracts:

```bash
source .venv/bin/activate
pytest backend/tests
```
