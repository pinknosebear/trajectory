from typing import Literal

from pydantic import BaseModel, Field

Window = Literal["7d", "14d", "30d", "90d"]


class Ring(BaseModel):
    key: str
    label: str
    current: float
    target: float
    unit: str
    pct: int
    on_track: bool
    trend: list[float]


class Overview(BaseModel):
    score: int | None
    delta: int | None
    rings: list[Ring]


class Kpi(BaseModel):
    key: str
    label: str
    value: float | int | None
    unit: str
    delta_pct: float | None
    good: bool | None
    type: str = "line"
    spark: list[float]


class GlucoseBand(BaseModel):
    lo: int
    hi: int


class GlucosePoint(BaseModel):
    date: str
    mean: int | None
    low: int | None
    high: int | None


class GlucoseSeries(BaseModel):
    window: Window
    band: GlucoseBand
    points: list[GlucosePoint]


class MealCurvePoint(BaseModel):
    ts: str
    mgdl: int


class MealInstance(BaseModel):
    meal_id: int
    meal: str
    meal_ts: str
    walked_after: bool
    baseline_mgdl: int | None
    peak_mgdl: int | None
    delta: int | None
    curve: list[MealCurvePoint]


class MealResponse(BaseModel):
    meal: str
    instances: list[MealInstance]


class Correlation(BaseModel):
    label: str
    r: float
    n: int
    note: str | None = None


class Checkin(BaseModel):
    id: int
    date: str
    mood: int
    energy: int
    stress: int
    note: str | None = None


class CheckinRequest(BaseModel):
    mood: int = Field(ge=1, le=5)
    energy: int = Field(ge=1, le=5)
    stress: int = Field(ge=1, le=5)
    note: str | None = Field(default=None, max_length=280)


class DashboardResponse(BaseModel):
    window: Window
    generated_at: str
    overview: Overview
    kpis: list[Kpi]
    glucose_series: GlucoseSeries
    meal_response: MealResponse
    correlations: list[Correlation]
    checkin_today: Checkin | None
