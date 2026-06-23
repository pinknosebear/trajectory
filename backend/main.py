"""Trajectory API — FastAPI over SQLite.

Endpoints (all GET, single participant):
  /api/briefing   latest AI weekly summary
  /api/goals      goal trajectory cards
  /api/meals/response?name=Rice%20%26%20dal   post-meal glucose comparison
  /api/labs?marker=eGFR                        lab trend

Run:  uvicorn main:app --reload
"""
import sqlite3
import datetime as dt
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

DB = Path(__file__).with_name("trajectory.db")
app = FastAPI(title="Trajectory API")


def db():
    if not DB.exists():
        raise HTTPException(500, "trajectory.db missing — run `python seed.py` first")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def curve_after(conn, meal_ts, hours=2):
    """The CGM points from a meal's start through +hours, for charting."""
    rows = conn.execute(
        "SELECT ts, mgdl FROM cgm_readings WHERE ts >= ? AND ts <= ?"
        " ORDER BY ts ASC",
        (meal_ts, _add_hours(meal_ts, hours)),
    ).fetchall()
    return [{"ts": r["ts"], "mgdl": r["mgdl"]} for r in rows]


def _add_hours(ts, hours):
    return (dt.datetime.fromisoformat(ts) + dt.timedelta(hours=hours)).isoformat(
        " ", "minutes"
    )


@app.get("/api/briefing")
def briefing():
    conn = db()
    row = conn.execute(
        "SELECT * FROM weekly_briefing ORDER BY week_start DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "no briefing yet")
    return dict(row)


@app.get("/api/goals")
def goals():
    conn = db()
    rows = conn.execute("SELECT * FROM goals ORDER BY id").fetchall()
    conn.close()
    out = []
    for r in rows:
        g = dict(r)
        g["trend"] = [float(x) for x in g["trend"].split(",")]
        g["on_track"] = bool(g["on_track"])
        out.append(g)
    return out


@app.get("/api/meals/response")
def meal_response(name: str = Query(..., description="Meal name to compare")):
    """Return every logged instance of a meal with its measured glucose response
    and the post-meal curve — the core 'what you ate, measured' insight."""
    conn = db()
    rows = conn.execute(
        "SELECT * FROM meal_glucose_response WHERE meal = ? ORDER BY meal_ts DESC",
        (name,),
    ).fetchall()
    if not rows:
        conn.close()
        raise HTTPException(404, f"no logged meals named {name!r}")
    out = []
    for r in rows:
        d = dict(r)
        d["walked_after"] = bool(d["walked_after"])
        d["delta"] = (
            d["peak_mgdl"] - d["baseline_mgdl"]
            if d["peak_mgdl"] is not None and d["baseline_mgdl"] is not None
            else None
        )
        d["curve"] = curve_after(conn, d["meal_ts"])
        out.append(d)
    conn.close()
    return {"meal": name, "instances": out}


@app.get("/api/labs")
def labs(marker: str = Query("eGFR")):
    conn = db()
    rows = conn.execute(
        "SELECT * FROM lab_results WHERE marker = ? ORDER BY ts ASC", (marker,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
