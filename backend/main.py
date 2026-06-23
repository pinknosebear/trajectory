import datetime as dt
from contextlib import closing

from fastapi import FastAPI, HTTPException, Query

from db import connect
from models import Checkin, CheckinRequest, DashboardResponse, GlucoseSeries, Kpi, Window
import queries

app = FastAPI(title="Trajectory API")


def _conn():
    return connect()


@app.get("/api/briefing")
def briefing():
    with closing(_conn()) as conn:
        row = queries.latest_briefing(conn)
    if not row:
        raise HTTPException(404, "no briefing yet")
    return row


@app.get("/api/goals")
def goals():
    with closing(_conn()) as conn:
        return queries.goals(conn)


@app.get("/api/meals/response")
def meal_response(name: str = Query(..., description="Meal name to compare")):
    with closing(_conn()) as conn:
        response = queries.meal_response(conn, name)
    if not response["instances"]:
        raise HTTPException(404, f"no logged meals named {name!r}")
    return response


@app.get("/api/labs")
def labs(marker: str = Query("eGFR")):
    with closing(_conn()) as conn:
        return queries.labs(conn, marker)


@app.get("/api/v1/dashboard", response_model=DashboardResponse)
def dashboard(window: Window = Query("7d")):
    with closing(_conn()) as conn:
        return {
            "window": window,
            "generated_at": dt.datetime.now().replace(microsecond=0).isoformat(),
            "overview": queries.overview(conn),
            "kpis": queries.kpis(conn, window),
            "glucose_series": queries.glucose_series(conn, "14d"),
            "meal_response": queries.meal_response(conn, "Rice & dal"),
            "correlations": queries.correlations(conn, "30d"),
            "checkin_today": queries.checkin_today(conn),
        }


@app.get("/api/v1/kpis", response_model=list[Kpi])
def kpis(window: Window = Query("7d")):
    with closing(_conn()) as conn:
        return queries.kpis(conn, window)


@app.get("/api/v1/glucose/series", response_model=GlucoseSeries)
def glucose_series(window: Window = Query("14d")):
    with closing(_conn()) as conn:
        return queries.glucose_series(conn, window)


@app.get("/api/v1/correlations")
def correlations(window: Window = Query("30d")):
    with closing(_conn()) as conn:
        return queries.correlations(conn, window)


@app.get("/api/v1/checkin/today", response_model=Checkin | None)
def checkin_today():
    with closing(_conn()) as conn:
        return queries.checkin_today(conn)


@app.post("/api/v1/checkin", response_model=Checkin)
def submit_checkin(payload: CheckinRequest):
    with closing(_conn()) as conn:
        return queries.upsert_checkin(conn, payload)
