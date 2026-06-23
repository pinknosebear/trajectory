# Trajectory — Web App

A real full-stack version of the Trajectory dashboard mockups: **FastAPI + SQLite** backend, **Vite + React** frontend. The HTML/JSX design files in the project are the visual target; this scaffold turns the strongest direction (Option C, "Your Coach") into a running app wired to real data.

```
SQLite ──> FastAPI (/api/*) ──> React (themeable components)
```

## What's here

```
trajectory-web/
├── backend/
│   ├── main.py            FastAPI app — goals, meals, briefing, labs endpoints
│   ├── schema.sql         Tables + the meal_glucose_response view (the core insight)
│   ├── seed.py            Loads sample data matching the mockups
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── package.json       Vite + React 18
    ├── vite.config.js     Proxies /api → localhost:8000
    └── src/
        ├── main.jsx
        ├── api.js         Tiny fetch wrapper
        ├── tokens.js      Design tokens (accent / surface / type) — themeable
        ├── App.jsx        Loads data, renders the dashboard
        ├── components/
        │   ├── Briefing.jsx       AI weekly summary hero
        │   ├── MealResponse.jsx   "what you ate, measured" — same meal, walk vs no-walk
        │   ├── Goals.jsx          Goal trajectory cards
        │   └── Sparkline.jsx      Inline SVG chart
        └── styles.css
```

## Run it

**Backend** (Python 3.10+):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py                 # creates trajectory.db with sample data
uvicorn main:app --reload      # → http://localhost:8000  (docs at /docs)
```

**Frontend** (Node 18+), in a second terminal:
```bash
cd frontend
npm install
npm run dev                    # → http://localhost:5173
```

The Vite dev server proxies `/api/*` to the backend, so the React app talks to FastAPI with no CORS setup.

## The data model

The heart of the product is the **meal → measured response** loop. The schema records each meal with a timestamp, and CGM readings are stored separately; the `meal_glucose_response` view joins them to compute the post-meal peak and whether a walk followed.

| table | what it holds |
|---|---|
| `cgm_readings` | timestamped glucose (mg/dL) from the sensor |
| `meals` | what was eaten, when, and whether a walk followed |
| `goals` | A1c / Time-in-Range / weight / steps with targets |
| `lab_results` | eGFR and other periodic draws |
| `weekly_briefing` | the AI-generated summary text (one row per week) |
| `meal_glucose_response` (view) | per-meal peak + delta, derived from the two tables above |

The AI weekly briefing is stored as text your generation job writes once a week — the frontend just renders the latest row. Swap the seed text for a real call to your model in `seed.py` / a scheduled job.

## Going further

- **Auth** — single-user today (your dad). Add a token check in `main.py` before exposing it beyond localhost.
- **Real device data** — replace `seed.py` with importers for CGM CSV / Apple Health export, writing into `cgm_readings` and `meals`.
- **Theming** — `tokens.js` mirrors the Tweaks panel from the mockups (accent, surface temperature, headline font). Wire it to a settings endpoint if you want it user-controlled.
- **The other two directions** — Option A (editorial) and Option B (mission-control dashboard) are in the project's JSX files; they share the same token shape, so they drop into this same data layer if you want to A/B them.
