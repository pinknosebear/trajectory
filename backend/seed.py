"""Seed trajectory.db with deterministic local-first health data."""

import argparse
import datetime as dt
import math
import random
import sqlite3
from pathlib import Path

from calculations import average_glucose, pearson_r, time_in_range

DB = Path(__file__).with_name("trajectory.db")
SCHEMA = Path(__file__).with_name("schema.sql")
RNG_SEED = 20260623


def _today():
    return dt.date.today()


def _dt(date_value, hour, minute=0):
    return dt.datetime.combine(date_value, dt.time(hour, minute))


def _meal_bump(minutes_from_meal, walked_after):
    if minutes_from_meal < 0 or minutes_from_meal > 150:
        return 0
    center = 55 if not walked_after else 45
    width = 38 if not walked_after else 30
    amplitude = 58 if not walked_after else 31
    return amplitude * math.exp(-((minutes_from_meal - center) ** 2) / (2 * width**2))


def _generate_day(conn, rng, date_value, day_index, cadence_minutes):
    sleep = max(4.8, min(8.5, 6.9 + rng.uniform(-0.65, 0.65) + 0.15 * math.sin(day_index / 8)))
    steps = int(max(2800, min(11200, 6500 + rng.gauss(0, 1100) + (sleep - 6.8) * 450)))
    hrv = int(max(24, min(58, 38 + (sleep - 6.8) * 4 + rng.gauss(0, 4))))
    weight = round(188.5 - day_index * 0.035 + rng.uniform(-0.35, 0.35), 1)
    stress_glucose = max(0, 7.1 - sleep) * 8 + max(0, 6400 - steps) / 900
    values = []

    for minute in range(0, 24 * 60, cadence_minutes):
        ts = dt.datetime.combine(date_value, dt.time()) + dt.timedelta(minutes=minute)
        circadian = 12 * math.sin((minute - 240) / 1440 * 2 * math.pi)
        base = 111 + circadian + stress_glucose + rng.gauss(0, 6)
        breakfast = _meal_bump(minute - 8 * 60, walked_after=False) * 0.45
        lunch = _meal_bump(minute - 12 * 60 - 45, walked_after=steps > 7000) * 0.55
        dinner_walk = day_index % 3 != 0
        dinner = _meal_bump(minute - 18 * 60 - 45, walked_after=dinner_walk)
        mgdl = int(round(max(68, min(235, base + breakfast + lunch + dinner))))
        values.append(mgdl)
        conn.execute(
            "INSERT INTO cgm_readings (ts, mgdl) VALUES (?, ?)",
            (ts.isoformat(" ", "minutes"), mgdl),
        )

    conn.execute(
        """
        INSERT INTO daily_metrics
          (date, steps, sleep_hrs, hrv_ms, avg_glucose, time_in_range, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            date_value.isoformat(),
            steps,
            round(sleep, 1),
            hrv,
            round(average_glucose(values)),
            round(time_in_range(values), 1),
            weight,
        ),
    )
    metric_rows = [
        ("steps", steps, "count", "seed"),
        ("sleep_hrs", round(sleep, 1), "hrs", "seed"),
        ("hrv_ms", hrv, "ms", "seed"),
        ("weight", weight, "lb", "seed"),
        ("avg_glucose", round(average_glucose(values)), "mg/dL", "seed"),
        ("time_in_range", round(time_in_range(values), 1), "%", "seed"),
    ]
    conn.executemany(
        """
        INSERT INTO metric_values (date, metric_key, value, unit, source)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(date_value.isoformat(), key, value, unit, source) for key, value, unit, source in metric_rows],
    )


def _insert_meal(conn, date_value, hour, minute, name, walked_after, note):
    conn.execute(
        "INSERT INTO meals (ts, name, walked_after, note) VALUES (?, ?, ?, ?)",
        (_dt(date_value, hour, minute).isoformat(" ", "minutes"), name, int(walked_after), note),
    )


def _seed_static_content(conn, today):
    rice_no_walk = today - dt.timedelta(days=6)
    rice_walk = today - dt.timedelta(days=5)
    _insert_meal(conn, rice_no_walk, 18, 52, "Rice & dal", False, "Standard portion, no walk after")
    _insert_meal(conn, rice_walk, 18, 48, "Rice & dal", True, "Same plate, 12-min walk after")
    _insert_meal(conn, today - dt.timedelta(days=11), 12, 35, "Chickpea bowl", True, "Lunch walk")
    _insert_meal(conn, today - dt.timedelta(days=18), 19, 10, "Pasta", False, "Late dinner")

    goals = [
        ("A1c", 7.1, 6.8, "%", 74, 1, "7.8,7.6,7.4,7.2,7.1"),
        ("Time in Range", 68, 75, "%", 68, 1, "56,59,62,64,68"),
        ("Weight", 185.4, 180, "lb", 56, 0, "189,188,187,186,185.4"),
        ("Steps", 6900, 8000, "", 61, 0, "5600,6100,6400,7100,6900"),
    ]
    conn.executemany(
        """
        INSERT INTO goals (label, current, target, unit, pct, on_track, trend)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        goals,
    )

    labs = [
        (today - dt.timedelta(days=132), "eGFR", 68, "mL/min"),
        (today - dt.timedelta(days=70), "eGFR", 64, "mL/min"),
        (today - dt.timedelta(days=14), "eGFR", 61, "mL/min"),
        (today - dt.timedelta(days=132), "A1c", 7.8, "%"),
        (today - dt.timedelta(days=70), "A1c", 7.4, "%"),
        (today - dt.timedelta(days=14), "A1c", 7.1, "%"),
    ]
    conn.executemany(
        "INSERT INTO lab_results (ts, marker, value, unit) VALUES (?, ?, ?, ?)",
        [(date.isoformat(), marker, value, unit) for date, marker, value, unit in labs],
    )

    week_start = today - dt.timedelta(days=today.weekday())
    conn.execute(
        """
        INSERT INTO weekly_briefing
          (week_start, headline, went_well, to_watch, doctor_q, experiment)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            week_start.isoformat(),
            "This was a steady week, Ravi - your glucose held in range more often than it has all spring.",
            "Time in Range rose to 68%, helped by calmer evenings after post-dinner walks.",
            "Sleep averaged under 7 hours, and the highest-glucose mornings followed shorter nights.",
            "Your eGFR has eased from 68 to 61 mL/min over three draws. Ask whether kidney function needs closer follow-up.",
            "Walk 15 minutes after dinner for 7 days and compare the evening glucose curve.",
        ),
    )

    snapshots = [
        (week_start - dt.timedelta(days=21), 59),
        (week_start - dt.timedelta(days=14), 61),
        (week_start - dt.timedelta(days=7), 63),
        (week_start, 65),
    ]
    conn.executemany(
        "INSERT INTO score_snapshots (week_start, score) VALUES (?, ?)",
        [(date.isoformat(), score) for date, score in snapshots],
    )

    checkins = [
        (today - dt.timedelta(days=1), 4, 3, 2, "Dinner walk helped."),
        (today - dt.timedelta(days=3), 3, 3, 4, "Short night."),
        (today - dt.timedelta(days=8), 4, 4, 2, "Felt steady."),
        (today - dt.timedelta(days=15), 2, 2, 5, "Work stress."),
    ]
    conn.executemany(
        "INSERT INTO check_ins (date, mood, energy, stress, note) VALUES (?, ?, ?, ?, ?)",
        [(date.isoformat(), mood, energy, stress, note) for date, mood, energy, stress, note in checkins],
    )


def _seed_correlations(conn, today):
    rows = conn.execute(
        """
        SELECT sleep_hrs, steps, hrv_ms, avg_glucose
        FROM daily_metrics
        WHERE date BETWEEN ? AND ?
        ORDER BY date ASC
        """,
        ((today - dt.timedelta(days=29)).isoformat(), today.isoformat()),
    ).fetchall()
    sleep = [row["sleep_hrs"] for row in rows]
    steps = [row["steps"] for row in rows]
    hrv = [row["hrv_ms"] for row in rows]
    glucose = [row["avg_glucose"] for row in rows]
    computed_at = dt.datetime.now().replace(microsecond=0).isoformat()
    correlations = [
        ("30d", "sleep_hrs", "avg_glucose", "More sleep -> lower glucose", pearson_r(sleep, glucose), len(rows), "Sleep averaged 6.8 hrs across the trailing window"),
        ("30d", "steps", "avg_glucose", "More steps -> lower glucose", pearson_r(steps, glucose), len(rows), "Higher-step days tended to have calmer evenings"),
        ("30d", "hrv_ms", "avg_glucose", "Higher HRV -> lower glucose", pearson_r(hrv, glucose), len(rows), "Recovery tracked modestly with glucose stability"),
    ]
    for window in ("7d", "14d", "90d"):
        for item in correlations:
            conn.execute(
                """
                INSERT INTO correlations_cache
                  (window, metric_key, outcome_key, label, r, n, note, computed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (window, item[1], item[2], item[3], round(item[4] or 0, 2), item[5], item[6], computed_at),
            )
    for item in correlations:
        conn.execute(
            """
            INSERT INTO correlations_cache
              (window, metric_key, outcome_key, label, r, n, note, computed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (item[0], item[1], item[2], item[3], round(item[4] or 0, 2), item[5], item[6], computed_at),
        )


def seed(mode):
    rng = random.Random(RNG_SEED)
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA.read_text())

    today = _today()
    days = 90 if mode == "full" else 35
    cadence = 5 if mode == "full" else 15
    start = today - dt.timedelta(days=days - 1)

    for offset in range(days):
        _generate_day(conn, rng, start + dt.timedelta(days=offset), offset, cadence)

    _seed_static_content(conn, today)
    _seed_correlations(conn, today)
    conn.commit()
    conn.close()
    print(f"Seeded {DB.name} with {days} days using --{mode}")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--full", action="store_true", help="Generate 90 days at 5-minute CGM cadence")
    group.add_argument("--fast", action="store_true", help="Generate a smaller deterministic dataset")
    args = parser.parse_args()
    seed("fast" if args.fast else "full")


if __name__ == "__main__":
    main()
