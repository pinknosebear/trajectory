import sqlite3
import datetime as dt
from pathlib import Path

from fastapi.testclient import TestClient

import db
import main
import seed


def _seed_tmp(tmp_path, monkeypatch):
    test_db = tmp_path / "trajectory-test.db"
    monkeypatch.setattr(db, "DB", test_db)
    monkeypatch.setattr(seed, "DB", test_db)
    seed.seed("fast")
    return test_db


def test_dashboard_response_contract(tmp_path, monkeypatch):
    _seed_tmp(tmp_path, monkeypatch)
    client = TestClient(main.app)

    response = client.get("/api/v1/dashboard?window=7d")

    assert response.status_code == 200
    body = response.json()
    assert body["window"] == "7d"
    assert body["overview"]["score"] is not None
    assert len(body["overview"]["rings"]) == 4
    assert len(body["kpis"]) == 6
    assert all("good" in kpi for kpi in body["kpis"])
    assert body["glucose_series"]["window"] == "14d"
    assert body["meal_response"]["meal"] == "Rice & dal"
    assert body["checkin_today"] is None


def test_checkin_upsert_behavior(tmp_path, monkeypatch):
    test_db = _seed_tmp(tmp_path, monkeypatch)
    client = TestClient(main.app)

    created = client.post(
        "/api/v1/checkin", json={"mood": 4, "energy": 3, "stress": 2, "note": "ok"}
    )
    updated = client.post(
        "/api/v1/checkin", json={"mood": 5, "energy": 4, "stress": 1, "note": "better"}
    )

    assert created.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["mood"] == 5
    with sqlite3.connect(Path(test_db)) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM check_ins WHERE date = ?",
            (dt.date.today().isoformat(),),
        ).fetchone()[0]
    assert count == 1
