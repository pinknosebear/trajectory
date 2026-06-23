-- Trajectory schema — single participant ("Ravi"), N-of-1 health data.
-- Stores raw device/lab data; derived insight (post-meal response) is a VIEW.

PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS meal_glucose_response;
DROP TABLE IF EXISTS cgm_readings;
DROP TABLE IF EXISTS meals;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS lab_results;
DROP TABLE IF EXISTS weekly_briefing;

-- Continuous glucose monitor: one row per reading (~every 5 min).
CREATE TABLE cgm_readings (
  id        INTEGER PRIMARY KEY,
  ts        TEXT    NOT NULL,          -- ISO8601 local time
  mgdl      INTEGER NOT NULL
);
CREATE INDEX idx_cgm_ts ON cgm_readings(ts);

-- Logged meals. `walked_after` captures the subjective/behavioral signal
-- wearables miss — the thing that makes the response comparison meaningful.
CREATE TABLE meals (
  id            INTEGER PRIMARY KEY,
  ts            TEXT    NOT NULL,       -- when eating started
  name          TEXT    NOT NULL,       -- e.g. "Rice & dal"
  walked_after  INTEGER NOT NULL DEFAULT 0,  -- 0/1
  note          TEXT
);
CREATE INDEX idx_meals_ts ON meals(ts);

-- Long-term goals with a current value and a target.
CREATE TABLE goals (
  id        INTEGER PRIMARY KEY,
  label     TEXT    NOT NULL,
  current   REAL    NOT NULL,
  target    REAL    NOT NULL,
  unit      TEXT    NOT NULL,
  pct       INTEGER NOT NULL,           -- progress 0-100
  on_track  INTEGER NOT NULL DEFAULT 1, -- 0/1
  -- recent trend as comma-separated values for the sparkline
  trend     TEXT    NOT NULL
);

-- Periodic lab draws (eGFR, etc.).
CREATE TABLE lab_results (
  id        INTEGER PRIMARY KEY,
  ts        TEXT    NOT NULL,
  marker    TEXT    NOT NULL,           -- e.g. "eGFR"
  value     REAL    NOT NULL,
  unit      TEXT    NOT NULL
);

-- One AI-written summary per week (your generation job writes these).
CREATE TABLE weekly_briefing (
  id            INTEGER PRIMARY KEY,
  week_start    TEXT    NOT NULL,
  headline      TEXT    NOT NULL,
  went_well     TEXT    NOT NULL,
  to_watch      TEXT    NOT NULL,
  doctor_q      TEXT,
  experiment    TEXT    NOT NULL
);

-- Derived: post-meal glucose response per meal.
-- Peak = max glucose in the 2 hours after the meal; baseline = reading at meal start.
CREATE VIEW meal_glucose_response AS
SELECT
  m.id            AS meal_id,
  m.name          AS meal,
  m.ts            AS meal_ts,
  m.walked_after  AS walked_after,
  (SELECT mgdl FROM cgm_readings c
     WHERE c.ts >= m.ts ORDER BY c.ts ASC LIMIT 1)            AS baseline_mgdl,
  (SELECT MAX(mgdl) FROM cgm_readings c
     WHERE c.ts >= m.ts
       AND c.ts <= datetime(m.ts, '+2 hours'))                AS peak_mgdl
FROM meals m;
