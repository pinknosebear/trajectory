# Trajectory — Product & Technical Design

**Status:** Canonical build spec  
**Surface:** Trajectory web app  
**Stack:** React, FastAPI, SQLite  
**Primary view:** Overview dashboard  
**Secondary view:** Coach briefing  

---

## 01. Product Intent

Trajectory is a personal health dashboard for understanding the relationship between daily behavior and metabolic outcomes. The app combines CGM readings, meals, goals, daily wearable-style metrics, lab trends, subjective check-ins, and weekly AI summaries into one calm, data-dense experience.

The product should help a returning user answer three questions in under five seconds:

- Am I on track?
- What changed this week?
- What should I pay attention to next?

The main product surface is the **Overview** dashboard: a mission-control view with goal progress, KPI changes, glucose trends, correlations, and a daily check-in. The existing **Coach** view remains available as a more narrative weekly briefing.

The app is currently single-participant and local-first. It should be built with production discipline, but implementation should stay appropriately scoped: durable data contracts, deterministic seed data, tested derivations, and clean component boundaries first; heavier infrastructure later.

---

## 02. Experience Principles

Trajectory should feel trustworthy, quiet, and usable repeatedly. It is not a marketing page and should not feel decorative for its own sake.

Core UX principles:

- **Dense but calm:** show enough information to scan the whole picture without visual noise.
- **Explain change:** every major number should include trend, delta, context, or comparison.
- **Prefer measured reality:** live API data should drive the UI; avoid hardcoded dashboard values.
- **Keep the user oriented:** Overview and Coach are sibling views over the same data layer.
- **Make empty states honest:** if data is insufficient, say so plainly instead of drawing misleading charts.
- **Preserve warmth:** use editorial type, restrained color, and human-readable copy without making the app feel clinical.

---

## 03. Visual Direction

The visual system is an editorial health dashboard:

- Dark fixed sidebar.
- Warm off-white app background.
- White or near-white panels.
- Terracotta primary accent by default.
- Green for favorable status and amber/red for caution.
- Serif display headings, sans-serif body text, and monospaced numerals.

Recommended type:

- Display: `Newsreader`
- Body: `Public Sans`
- Mono: `IBM Plex Mono`

Recommended token families:

```js
{
  bg,
  paper,
  panel,
  ink,
  ink2,
  soft,
  faint,
  line,
  accent,
  accentSoft,
  accentDeep,
  onAccent,
  good,
  warn,
  sidebar,
  sidebarInk,
  display,
  body,
  mono
}
```

Design constraints:

- Sidebar width is `212px`.
- Cards use modest radii, generally `6px` to `8px`.
- No nested cards.
- No decorative gradient blobs or ornamental background shapes.
- Charts should be readable first, beautiful second.
- Numeric values, deltas, and scores should use the mono font.
- Headings should use the display font.
- Body labels, notes, nav, and supporting text should use the body font.

---

## 04. Overview Layout

Overview uses a two-column shell: fixed sidebar plus fluid main content. The main region stacks a page header, a goal summary band, a KPI grid, and a lower split region for charts plus insights.

```text
┌──────────────┬──────────────────────────────────────────────────┐
│  ▣ Trajectory│  Overview                         [+ Check-in]    │
│              │  Tuesday, June 23 · last 7d vs prior 7d           │
│ ▸ Overview   │ ┌──────────────────────────────────────────────┐ │
│   Coach      │ │ 68% ▲4   ◔ A1c  ◔ TIR  ◔ Weight  ◔ Steps     │ │
│   Goals      │ └──────────────────────────────────────────────┘ │
│   Glucose    │ ┌────────┐┌────────┐┌────────┐                   │
│   Labs       │ │AvgGluc ││  TIR   ││  GMI   │                   │
│   Trends     │ │  142   ││  64%   ││  7.1   │                   │
│   Experiments│ ├────────┤├────────┤├────────┤                   │
│   Daily Log  │ │ Steps  ││ Sleep  ││  HRV   │                   │
│              │ │  6.2k  ││  6.8   ││   38   │                   │
│              │ └────────┘└────────┘└────────┘                   │
│              │ ┌─────────────────────────┐ ┌──────────────────┐ │
│              │ │ Glucose · 14/30/90d     │ │ Correlations     │ │
│              │ │ line + target band      │ │ sleep -> glucose │ │
│              │ ├─────────────────────────┤ ├──────────────────┤ │
│              │ │ Post-meal response      │ │ Today's check-in │ │
│ ◍ Ravi       │ └─────────────────────────┘ └──────────────────┘ │
└──────────────┴──────────────────────────────────────────────────┘
```

Regions:

| Region | Purpose |
|---|---|
| Sidebar | App navigation, product mark, profile chip |
| Header | Page title, comparison window, check-in action |
| Goal band | Composite score and four goal rings |
| KPI grid | Six current health metrics with deltas and sparklines |
| Glucose chart | Daily glucose mean across selectable windows |
| Meal response | Reused post-meal comparison chart |
| Correlations | Ranked behavior/outcome relationships |
| Check-in | Mood, energy, stress logging |

Desktop is the primary target. The first supported responsive breakpoint is `>= 1024px`; smaller layouts may degrade gracefully until a mobile-specific design is created.

---

## 05. Navigation Model

Top-level views:

- Overview
- Coach
- Goals
- Glucose
- Labs
- Trends
- Correlations
- Experiments
- Daily Log
- Learn
- Weekly Summary

For the first milestone, only Overview and Coach need to be functional. Other nav items should render as inert or disabled controls, not broken links.

Sidebar behavior:

- Fixed width: `212px`.
- Full viewport height.
- Background: `t.sidebar`.
- Text: `t.sidebarInk`.
- Active nav item: translucent white fill, white text, semibold weight.
- Profile chip pinned to the bottom.

---

## 06. Data Model

The app stores raw observations, derived rollups, subjective check-ins, and cached summaries.

Existing core tables:

```sql
CREATE TABLE cgm_readings (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  mgdl INTEGER NOT NULL
);

CREATE TABLE meals (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  name TEXT NOT NULL,
  walked_after INTEGER NOT NULL DEFAULT 0,
  note TEXT
);

CREATE TABLE goals (
  id INTEGER PRIMARY KEY,
  label TEXT NOT NULL,
  current REAL NOT NULL,
  target REAL NOT NULL,
  unit TEXT NOT NULL,
  pct INTEGER NOT NULL,
  on_track INTEGER NOT NULL DEFAULT 1,
  trend TEXT NOT NULL
);

CREATE TABLE lab_results (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  marker TEXT NOT NULL,
  value REAL NOT NULL,
  unit TEXT NOT NULL
);

CREATE TABLE weekly_briefing (
  id INTEGER PRIMARY KEY,
  week_start TEXT NOT NULL,
  headline TEXT NOT NULL,
  went_well TEXT NOT NULL,
  to_watch TEXT NOT NULL,
  doctor_q TEXT,
  experiment TEXT NOT NULL
);
```

Required new tables:

```sql
CREATE TABLE daily_metrics (
  date TEXT PRIMARY KEY,
  steps INTEGER,
  sleep_hrs REAL,
  hrv_ms INTEGER,
  avg_glucose INTEGER,
  time_in_range REAL,
  CHECK (sleep_hrs IS NULL OR sleep_hrs >= 0),
  CHECK (time_in_range IS NULL OR (time_in_range >= 0 AND time_in_range <= 100))
);

CREATE TABLE check_ins (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL UNIQUE,
  mood INTEGER NOT NULL CHECK (mood BETWEEN 1 AND 5),
  energy INTEGER NOT NULL CHECK (energy BETWEEN 1 AND 5),
  stress INTEGER NOT NULL CHECK (stress BETWEEN 1 AND 5),
  note TEXT
);

CREATE TABLE score_snapshots (
  week_start TEXT PRIMARY KEY,
  score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100)
);

CREATE TABLE metric_values (
  id INTEGER PRIMARY KEY,
  date TEXT NOT NULL,
  metric_key TEXT NOT NULL,
  value REAL,
  unit TEXT,
  source TEXT,
  UNIQUE(date, metric_key)
);

CREATE TABLE correlations_cache (
  id INTEGER PRIMARY KEY,
  window TEXT NOT NULL,
  metric_key TEXT NOT NULL,
  outcome_key TEXT NOT NULL,
  label TEXT NOT NULL,
  r REAL NOT NULL,
  n INTEGER NOT NULL,
  note TEXT,
  computed_at TEXT NOT NULL,
  UNIQUE(window, metric_key, outcome_key)
);
```

Required indexes:

```sql
CREATE INDEX IF NOT EXISTS idx_cgm_ts ON cgm_readings(ts);
CREATE INDEX IF NOT EXISTS idx_meals_ts ON meals(ts);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);
CREATE INDEX IF NOT EXISTS idx_metric_values_key_date ON metric_values(metric_key, date);
CREATE INDEX IF NOT EXISTS idx_correlations_cache_window ON correlations_cache(window);
```

`metric_values` exists to absorb future metrics without requiring a schema migration for every new signal. `daily_metrics` remains the fast, typed table for first-class Overview metrics.

---

## 07. Derived Metrics

All derivations should live in testable backend helper functions.

Definitions:

- **Average glucose:** mean `mgdl` over the selected window.
- **Time in range:** percent of CGM readings where `70 <= mgdl <= 180`.
- **GMI:** `3.31 + 0.02392 * mean_glucose_mgdl`.
- **Percent delta:** `(current_window - prior_window) / prior_window * 100`.
- **Composite score:** rounded mean of goal `pct` values with nulls excluded.
- **Correlation:** Pearson `r` across paired daily series over a trailing window.

Metric direction:

| Metric | Favorable direction |
|---|---|
| Avg glucose | Lower |
| GMI | Lower |
| Weight | Lower or goal-dependent |
| Time in range | Higher |
| Steps | Higher |
| Sleep | Higher within reasonable bounds |
| HRV | Higher |
| Mood | Higher |
| Energy | Higher |
| Stress | Lower |

The API should return explicit `good` booleans for deltas. The frontend should not infer whether a signed delta is favorable based only on the sign.

---

## 08. API Design

The canonical Overview endpoint is:

```http
GET /api/v1/dashboard?window=7d
```

Supported windows:

- `7d`
- `14d`
- `30d`
- `90d`

The dashboard response should be one consistent snapshot:

```json
{
  "window": "7d",
  "generated_at": "2026-06-23T09:15:00",
  "overview": {
    "score": 68,
    "delta": 4,
    "rings": [
      {
        "key": "a1c",
        "label": "A1c",
        "current": 7.1,
        "target": 6.8,
        "unit": "%",
        "pct": 74,
        "on_track": true,
        "trend": [7.8, 7.6, 7.4, 7.2, 7.1]
      }
    ]
  },
  "kpis": [
    {
      "key": "avg_glucose",
      "label": "Avg Glucose",
      "value": 142,
      "unit": "mg/dL",
      "delta_pct": -4.1,
      "good": true,
      "type": "line",
      "spark": [156, 150, 152, 147, 145, 142]
    }
  ],
  "glucose_series": {
    "window": "14d",
    "band": { "lo": 70, "hi": 180 },
    "points": [
      { "date": "2026-06-09", "mean": 151, "low": 88, "high": 198 }
    ]
  },
  "meal_response": {
    "meal": "Rice & dal",
    "instances": []
  },
  "correlations": [
    {
      "label": "More sleep -> lower glucose",
      "r": -0.42,
      "n": 30,
      "note": "Sleep averaged 6.8 hrs across the trailing window"
    }
  ],
  "checkin_today": null
}
```

Keep smaller endpoints for view-specific or drilldown use:

```http
GET  /api/briefing
GET  /api/goals
GET  /api/meals/response?name=Rice%20%26%20dal
GET  /api/labs?marker=eGFR

GET  /api/v1/kpis?window=7d
GET  /api/v1/glucose/series?window=14d
GET  /api/v1/correlations?window=30d
GET  /api/v1/checkin/today
POST /api/v1/checkin
```

Check-in request:

```json
{
  "mood": 4,
  "energy": 3,
  "stress": 2,
  "note": "Optional short note"
}
```

API implementation requirements:

- Use parameterized SQL.
- Validate request and response shapes with Pydantic models.
- Return empty arrays or `null` for missing optional data where appropriate.
- Use `404` only when a requested resource truly does not exist.
- Include clear errors when the local database has not been seeded.

---

## 09. Backend Architecture

The backend should stay simple while isolating responsibilities.

Recommended structure:

```text
backend/
  main.py              FastAPI app and route registration
  db.py                SQLite connection helpers
  models.py            Pydantic request/response models
  calculations.py      GMI, TIR, deltas, score, Pearson r
  queries.py           SQL query helpers
  rollups.py           daily rollup and correlation cache jobs
  seed.py              deterministic local dataset generation
  schema.sql           current schema for local database creation
  tests/
    test_calculations.py
    test_dashboard_api.py
```

The first implementation may keep some of this inside `main.py`, but extraction should happen as soon as endpoint logic grows beyond thin request/response handling.

Background jobs:

- **Daily rollup job:** computes `daily_metrics.avg_glucose` and `daily_metrics.time_in_range`.
- **Score snapshot job:** computes weekly composite score into `score_snapshots`.
- **Correlation job:** computes rolling correlations into `correlations_cache`.

For local development, these jobs can be explicit Python functions run by `seed.py` or a manual command. A scheduler can be added later.

---

## 10. Seed Data

Seed data must be deterministic, idempotent, and realistic enough to exercise the dashboard.

Requirements:

- Use a fixed random seed.
- Generate at least 90 days of CGM readings.
- Use approximately 5-minute CGM cadence.
- Generate matching `daily_metrics` rows for each day.
- Include representative meals with post-meal CGM curves.
- Include goal rows for A1c, Time in Range, Weight, and Steps.
- Include lab trend rows.
- Include weekly briefing rows.
- Include several check-ins, including a case where today has no check-in.
- Support a fast seed mode for tests and CI.

Expected full seed size:

- 90 days * 288 CGM readings per day = about 25,920 CGM rows.
- At least 90 `daily_metrics` rows.

Seed command targets:

```bash
python backend/seed.py --full
python backend/seed.py --fast
```

---

## 11. Frontend Architecture

Recommended structure:

```text
frontend/src/
  api.js
  tokens.js
  App.jsx
  components/
    Sidebar.jsx
    Overview.jsx
    Coach.jsx
    GoalRingBand.jsx
    KpiCard.jsx
    KpiGrid.jsx
    GlucoseChart.jsx
    CorrelationList.jsx
    CheckinCard.jsx
    Briefing.jsx
    MealResponse.jsx
    Goals.jsx
    primitives/
      Ring.jsx
      Sparkline.jsx
      Bars.jsx
      Dots.jsx
      MealCurve.jsx
```

State strategy:

- First milestone: `useEffect` plus local state is acceptable.
- Preferred next step: TanStack Query for caching, retries, revalidation, and check-in mutation state.
- Keep dashboard data fetching centralized so all Overview regions render from the same snapshot.

Charting:

- Use Recharts for the main glucose chart.
- Use small custom SVG primitives for rings, sparklines, bars, dots, and meal curves.

Required frontend states:

- Loading.
- Per-region empty data.
- Per-region error where practical.
- Full-page backend unavailable error.
- Check-in empty state.
- Check-in submitting state.
- Check-in logged state.

---

## 12. Component Contracts

Primitive components:

| Component | Purpose | Required props |
|---|---|---|
| `Ring` | Circular progress | `pct`, `color`, `track`, `size`, `stroke`, `children` |
| `Sparkline` | Small KPI trend | `data`, `color`, `w`, `h`, `dot` |
| `Bars` | Small bar trend | `data`, `color`, `w`, `h` |
| `Dots` | 1-5 check-in scale | `value`, `onChange`, `readonly`, `color` |
| `MealCurve` | Post-meal response | `data`, `band`, `line2`, `line2color` |

Composite components:

| Component | Purpose |
|---|---|
| `Sidebar` | Shared navigation shell |
| `Overview` | Dashboard page container |
| `GoalRingBand` | Composite score and goal rings |
| `KpiGrid` | Six dashboard KPI cards |
| `GlucoseChart` | Daily glucose series with 14/30/90 controls |
| `CorrelationList` | Ranked insights |
| `CheckinCard` | Daily mood/energy/stress flow |
| `Coach` | Narrative briefing view |

Component rules:

- Components receive data as props and do not hardcode health values.
- Components receive tokens or consume a central token context.
- Small charts must handle empty arrays.
- Interactive controls must be keyboard reachable.
- Buttons should use native `button` elements.

---

## 13. Overview Region Specs

### Header

Content:

- Title: `Overview`
- Subtitle: `{weekday}, {month} {day} · last 7d vs prior 7d`
- Button: `+ Check-in`

Behavior:

- Check-in button scrolls or focuses the check-in card.

### Goal Band

Content:

- Composite score from goal percentages.
- Weekly delta from `score_snapshots`.
- Four rings: A1c, Time in Range, Weight, Steps.

Behavior:

- Ring color uses `good` when on track, `warn` when not.
- If no prior score exists, show neutral copy instead of a fake delta.

### KPI Grid

Six tiles:

- Avg Glucose
- Time in Range
- GMI
- Steps
- Sleep
- HRV

Each tile shows:

- Label.
- Definition tooltip affordance.
- Delta percent vs prior window.
- Current value and unit.
- Sparkline or bars.

### Glucose Chart

Content:

- Daily mean glucose.
- 70-180 mg/dL target band.
- Selectable windows: 14d, 30d, 90d.

Behavior:

- Switching windows reuses cached data when available.
- Empty data renders a clear empty state.

### Meal Response

Content:

- Existing meal comparison data.
- Baseline, peak, delta, and curve.
- Walk-after-meal comparison when available.

### Correlations

Content:

- Two to four ranked insights.
- Plain-language label.
- Pearson coefficient.
- Sample size or supporting note.

Behavior:

- Sort by absolute `r` descending.
- Hide weak or underpowered correlations unless needed for an empty state.

### Check-In

Content:

- Mood 1-5.
- Energy 1-5.
- Stress 1-5.
- Optional note later; not required in first UI.

Behavior:

- Load today on page load.
- If present, display logged state.
- If absent, allow dot selection and POST.
- After submit, re-fetch today and render persisted state.

---

## 14. Testing Strategy

Backend tests:

- GMI formula.
- Time in range calculation.
- Percent delta behavior with zero or missing prior window.
- Composite score with missing values.
- Pearson correlation.
- Dashboard endpoint contract.
- Check-in upsert behavior.

Frontend tests:

- Overview renders with a representative dashboard payload.
- KPI cards choose line vs bar correctly.
- Check-in submit calls the expected API and renders logged state.
- Empty chart data renders the empty state.

Manual QA:

- Backend missing database error is understandable.
- Overview loads without console errors.
- Coach view still works.
- 14/30/90 glucose switching works.
- No hardcoded dashboard values remain in Overview components.
- Re-theming through tokens affects sidebar, cards, charts, and buttons.

---

## 15. Performance And Reliability

Local-first requirements:

- Dashboard endpoint should respond quickly with seeded data.
- Heavy calculations should be precomputed where practical.