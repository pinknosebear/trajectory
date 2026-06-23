-- Trajectory schema - single participant local-first health data.

PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS meal_glucose_response;
DROP TABLE IF EXISTS correlations_cache;
DROP TABLE IF EXISTS metric_values;
DROP TABLE IF EXISTS score_snapshots;
DROP TABLE IF EXISTS check_ins;
DROP TABLE IF EXISTS daily_metrics;
DROP TABLE IF EXISTS weekly_briefing;
DROP TABLE IF EXISTS lab_results;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS meals;
DROP TABLE IF EXISTS cgm_readings;

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

CREATE TABLE daily_metrics (
  date TEXT PRIMARY KEY,
  steps INTEGER,
  sleep_hrs REAL,
  hrv_ms INTEGER,
  avg_glucose INTEGER,
  time_in_range REAL,
  weight REAL,
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

CREATE INDEX IF NOT EXISTS idx_cgm_ts ON cgm_readings(ts);
CREATE INDEX IF NOT EXISTS idx_meals_ts ON meals(ts);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);
CREATE INDEX IF NOT EXISTS idx_metric_values_key_date ON metric_values(metric_key, date);
CREATE INDEX IF NOT EXISTS idx_correlations_cache_window ON correlations_cache(window);

CREATE VIEW meal_glucose_response AS
SELECT
  m.id AS meal_id,
  m.name AS meal,
  m.ts AS meal_ts,
  m.walked_after AS walked_after,
  (SELECT mgdl FROM cgm_readings c
     WHERE c.ts >= m.ts ORDER BY c.ts ASC LIMIT 1) AS baseline_mgdl,
  (SELECT MAX(mgdl) FROM cgm_readings c
     WHERE c.ts >= m.ts
       AND c.ts <= datetime(m.ts, '+2 hours')) AS peak_mgdl
FROM meals m;