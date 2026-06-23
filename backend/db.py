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