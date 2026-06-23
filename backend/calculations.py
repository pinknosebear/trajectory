import math
from statistics import mean


def average_glucose(values):
    clean = [v for v in values if v is not None]
    return mean(clean) if clean else None


def time_in_range(values, lo=70, hi=180):
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    in_range = sum(1 for v in clean if lo <= v <= hi)
    return in_range / len(clean) * 100


def gmi(mean_glucose_mgdl):
    if mean_glucose_mgdl is None:
        return None
    return 3.31 + 0.02392 * mean_glucose_mgdl


def percent_delta(current, prior):
    if current is None or prior in (None, 0):
        return None
    return (current - prior) / prior * 100


def composite_score(pcts):
    clean = [p for p in pcts if p is not None]
    if not clean:
        return None
    return round(mean(clean))


def pearson_r(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 2:
        return None
backend/db.py
Full file content failed to load
import sqlite3
from pathlib import Path

from fastapi import HTTPException

DB = Path(__file__).with_name("trajectory.db")


def connect(db_path: Path | str = DB) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.exists():
        raise HTTPException(
            500,
            f"{path.name} missing - run `python backend/seed.py --full` first",
        )
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn