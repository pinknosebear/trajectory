"""Seed trajectory.db with sample data matching the design mockups.

Run once:  python seed.py
Re-running rebuilds the DB from scratch (schema.sql drops + recreates).
"""
import sqlite3
import datetime as dt
from pathlib import Path

DB = Path(__file__).with_name("trajectory.db")
SCHEMA = Path(__file__).with_name("schema.sql")


def synth_cgm_curve(conn, start_iso, peak, baseline=92):
    """Insert a realistic ~2h post-meal glucose curve, 8 points, 15 min apart.

    Curve rises to `peak` around 45-60 min then settles back toward baseline.
    Shape is the same one the MealResponse component draws.
    """
    start = dt.datetime.fromisoformat(start_iso)
    rise = peak - baseline
    # fractions of the rise at each 15-min step
    shape = [0.0, 0.35, 0.85, 1.0, 0.82, 0.5, 0.26, 0.11]
    for i, frac in enumerate(shape):
        ts = (start + dt.timedelta(minutes=15 * i)).isoformat(" ", "minutes")
        conn.execute(
            "INSERT INTO cgm_readings (ts, mgdl) VALUES (?, ?)",
            (ts, round(baseline + rise * frac)),
        )


def main():
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA.read_text())

    # ── Two same-meal dinners: Wed (no walk, peak 178) vs Thu (walk, peak 142)
    conn.execute(
        "INSERT INTO meals (ts, name, walked_after, note) VALUES (?,?,?,?)",
        ("2026-06-17 18:52", "Rice & dal", 0, "Standard portion, no walk after"),
    )
    synth_cgm_curve(conn, "2026-06-17 18:52", peak=178)

    conn.execute(
        "INSERT INTO meals (ts, name, walked_after, note) VALUES (?,?,?,?)",
        ("2026-06-18 18:48", "Rice & dal", 1, "Same plate, 12-min walk after"),
    )
    synth_cgm_curve(conn, "2026-06-18 18:48", peak=142)

    # ── Goals (current → target, progress, recent trend for sparkline)
    goals = [
        ("A1c", 7.4, 7.0, "%", 55, 1, "7.9,7.8,7.7,7.6,7.5,7.4"),
        ("Time in Range", 64, 70, "%", 62, 1, "54,57,59,58,62,64"),
        ("Weight", 187, 180, "lb", 41, 0, "192,191,190,189,188,187"),
        ("Steps", 6200, 8000, "", 48, 0, "5200,5800,5400,6600,6000,6200"),
    ]
    conn.executemany(
        "INSERT INTO goals (label,current,target,unit,pct,on_track,trend)"
        " VALUES (?,?,?,?,?,?,?)",
        goals,
    )

    # ── Lab results: eGFR easing over three draws
    labs = [
        ("2026-02-10", "eGFR", 68, "mL/min"),
        ("2026-04-14", "eGFR", 64, "mL/min"),
        ("2026-06-09", "eGFR", 61, "mL/min"),
    ]
    conn.executemany(
        "INSERT INTO lab_results (ts,marker,value,unit) VALUES (?,?,?,?)", labs
    )

    # ── This week's AI briefing
    conn.execute(
        "INSERT INTO weekly_briefing"
        " (week_start, headline, went_well, to_watch, doctor_q, experiment)"
        " VALUES (?,?,?,?,?,?)",
        (
            "2026-06-16",
            "This was a steady week, Ravi — your glucose held in range more "
            "often than it has all spring.",
            "Time in Range rose to 64%, up from 58% last week. Your three "
            "post-dinner walks lined up with the calmest evening glucose "
            "curves you've logged all year.",
            "Sleep slipped to 6.8 hrs, and your two highest-glucose mornings "
            "both followed short nights. Worth protecting your bedtime.",
            "Your eGFR has eased from 68 to 61 mL/min over three draws. Worth "
            "asking whether it warrants a closer look at kidney function.",
            "Walk 15 minutes after dinner, every night for 7 days — and "
            "measure the difference.",
        ),
    )

    conn.commit()
    conn.close()
    print(f"Seeded {DB.name}")


if __name__ == "__main__":
    main()
