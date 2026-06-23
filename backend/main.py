import base64
import datetime as dt
import os
import secrets
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.staticfiles import StaticFiles

from db import connect
from models import Checkin, CheckinRequest, DashboardResponse, GlucoseSeries, Kpi, Window
import queries

app = FastAPI(title="Trajectory API")

# Optional shared-password gate. When DEMO_PASSWORD is set the whole app
# (API + frontend) sits behind HTTP Basic auth; any username is accepted.
# Unset (e.g. local dev) leaves everything open.
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD")


@app.middleware("http")
async def password_gate(request: Request, call_next):
    if DEMO_PASSWORD:
        header = request.headers.get("authorization", "")
        supplied = ""
        if header.startswith("Basic "):
            try:
                _, _, supplied = base64.b64decode(header[6:]).decode().partition(":")
            except Exception:
                supplied = ""
        if not secrets.compare_digest(supplied, DEMO_PASSWORD):
            return Response(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Trajectory"'},
            )
    return await call_next(request)


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


# Serve the built React app, if present (production / Docker). Mounted last so
# the /api routes above take precedence. html=True serves index.html at "/".
STATIC_DIR = Path(__file__).with_name("static")
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
