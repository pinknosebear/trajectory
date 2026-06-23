import datetime as dt

from calculations import composite_score, gmi, percent_delta

WINDOW_DAYS = {"7d": 7, "14d": 14, "30d": 30, "90d": 90}


def window_dates(window: str, end: dt.date | None = None):
    days = WINDOW_DAYS[window]
    end_date = end or dt.date.today()
    start_date = end_date - dt.timedelta(days=days - 1)
    prior_end = start_date - dt.timedelta(days=1)
    prior_start = prior_end - dt.timedelta(days=days - 1)
    return start_date, end_date, prior_start, prior_end


def _iso(date_value: dt.date):
    return date_value.isoformat()


def goals(conn):
    rows = conn.execute("SELECT * FROM goals ORDER BY id").fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["trend"] = [float(x) for x in item["trend"].split(",") if x]
        item["on_track"] = bool(item["on_track"])
        out.append(item)
    return out


def latest_briefing(conn):
    row = conn.execute(
        "SELECT * FROM weekly_briefing ORDER BY week_start DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def labs(conn, marker: str):
    rows = conn.execute(
        "SELECT * FROM lab_results WHERE marker = ? ORDER BY ts ASC", (marker,)
    ).fetchall()
    return [dict(row) for row in rows]


def curve_after(conn, meal_ts: str, hours: int = 2):
    end_ts = (
        dt.datetime.fromisoformat(meal_ts) + dt.timedelta(hours=hours)
    ).isoformat(" ", "minutes")
    rows = conn.execute(
        """
        SELECT ts, mgdl
        FROM cgm_readings
        WHERE ts >= ? AND ts <= ?
        ORDER BY ts ASC
        """,
        (meal_ts, end_ts),
    ).fetchall()
    return [{"ts": row["ts"], "mgdl": row["mgdl"]} for row in rows]


def meal_response(conn, name: str):
    rows = conn.execute(
        """
        SELECT *
        FROM meal_glucose_response
        WHERE meal = ?
        ORDER BY meal_ts DESC
        """,
        (name,),
    ).fetchall()
    instances = []
    for row in rows:
        item = dict(row)
        item["walked_after"] = bool(item["walked_after"])
        item["delta"] = (
            item["peak_mgdl"] - item["baseline_mgdl"]
            if item["peak_mgdl"] is not None and item["baseline_mgdl"] is not None
            else None
        )
        item["curve"] = curve_after(conn, item["meal_ts"])
        instances.append(item)
    return {"meal": name, "instances": instances}


def _daily_rows(conn, start: dt.date, end: dt.date):
    rows = conn.execute(
        """
        SELECT *
        FROM daily_metrics
        WHERE date BETWEEN ? AND ?
        ORDER BY date ASC
        """,
        (_iso(start), _iso(end)),
    ).fetchall()
    return [dict(row) for row in rows]


def _avg(rows, key):
    values = [row[key] for row in rows if row.get(key) is not None]
    return sum(values) / len(values) if values else None


def _round(value, digits=1):
    if value is None:
        return None
    rounded = round(value, digits)
    return int(rounded) if float(rounded).is_integer() else rounded


def overview(conn):
    rings = goals(conn)
    current_score = composite_score([ring["pct"] for ring in rings])
    row = conn.execute(
        "SELECT score FROM score_snapshots ORDER BY week_start DESC LIMIT 1 OFFSET 1"
    ).fetchone()
    prior_score = row["score"] if row else None
    return {
        "score": current_score,
        "delta": current_score - prior_score
        if current_score is not None and prior_score is not None
        else None,
        "rings": [
            {
                "key": ring["label"].lower().replace(" ", "_"),
                "label": ring["label"],
                "current": ring["current"],
                "target": ring["target"],
                "unit": ring["unit"],
                "pct": ring["pct"],
                "on_track": ring["on_track"],
                "trend": ring["trend"],
            }
            for ring in rings
        ],
    }


def kpis(conn, window: str):
    start, end, prior_start, prior_end = window_dates(window)
    current = _daily_rows(conn, start, end)
    prior = _daily_rows(conn, prior_start, prior_end)

    def build(key, label, unit, direction, transform=lambda x: x, digits=1):
        current_value = transform(_avg(current, key))
        prior_value = transform(_avg(prior, key))
        delta = percent_delta(current_value, prior_value)
        good = None
        if delta is not None:
            good = delta >= 0 if direction == "higher" else delta <= 0
        spark = [row[key] for row in current if row.get(key) is not None]
        return {
            "key": key if key != "time_in_range" else "tir",
            "label": label,
            "value": _round(current_value, digits),
            "unit": unit,
            "delta_pct": _round(delta, 1),
            "good": good,
            "type": "line",
            "spark": [_round(v, digits) for v in spark],
        }

    avg_glucose = build("avg_glucose", "Avg Glucose", "mg/dL", "lower", digits=0)
    tir = build("time_in_range", "Time in Range", "%", "higher", digits=0)
    gmi_kpi = build(
        "avg_glucose", "GMI", "%", "lower", transform=lambda value: gmi(value), digits=1
    )
    gmi_kpi["key"] = "gmi"
    steps = build("steps", "Steps", "", "higher", digits=0)
    sleep = build("sleep_hrs", "Sleep", "hrs", "higher", digits=1)
    hrv = build("hrv_ms", "HRV", "ms", "higher", digits=0)
    return [avg_glucose, tir, gmi_kpi, steps, sleep, hrv]


def glucose_series(conn, window: str):
    start, end, _, _ = window_dates(window)
    rows = conn.execute(
        """
        SELECT
          date(ts) AS date,
          ROUND(AVG(mgdl)) AS mean,
          MIN(mgdl) AS low,
          MAX(mgdl) AS high
        FROM cgm_readings
        WHERE date(ts) BETWEEN ? AND ?
        GROUP BY date(ts)
        ORDER BY date(ts) ASC
        """,
        (_iso(start), _iso(end)),
    ).fetchall()
    return {
        "window": window,
        "band": {"lo": 70, "hi": 180},
        "points": [
            {
                "date": row["date"],
                "mean": row["mean"],
                "low": row["low"],
                "high": row["high"],
            }
            for row in rows
        ],
    }


def correlations(conn, window: str):
    rows = conn.execute(
        """
        SELECT label, r, n, note
        FROM correlations_cache
        WHERE window = ?
        ORDER BY ABS(r) DESC, id ASC
        """,
        (window,),
    ).fetchall()
    return [dict(row) for row in rows]


def checkin_today(conn, today: dt.date | None = None):
    date_value = (today or dt.date.today()).isoformat()
    row = conn.execute("SELECT * FROM check_ins WHERE date = ?", (date_value,)).fetchone()
    return dict(row) if row else None


def upsert_checkin(conn, payload, today: dt.date | None = None):
    date_value = (today or dt.date.today()).isoformat()
    conn.execute(
        """
        INSERT INTO check_ins (date, mood, energy, stress, note)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
          mood = excluded.mood,
          energy = excluded.energy,
          stress = excluded.stress,
          note = excluded.note
        """,
        (date_value, payload.mood, payload.energy, payload.stress, payload.note),
    )
    conn.commit()
    return checkin_today(conn, today)
