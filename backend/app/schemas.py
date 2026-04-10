from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


# ── Flights ───────────────────────────────────────────────────────────────────

class GpsPoint(BaseModel):
    lat: float
    lon: float
    alt: float
    t: int  # seconds from start


class TelemetrySample(BaseModel):
    t: int
    alt_m: float
    speed_ms: float
    batt_pct: float
    rc_signal: float
    video_signal: float
    gps_signal: float
    heading_deg: float
    dist_home_m: float
    temp_c: float


class FlightTag(BaseModel):
    label: str
    kind: str  # night | speed | warn | normal | ok


class FlightCreate(BaseModel):
    drone_model: str
    battery_serial: Optional[str] = None
    date: datetime
    duration_sec: int
    distance_km: float
    max_alt_m: float
    max_speed_ms: float
    batt_start_pct: int
    batt_end_pct: int
    home_lat: Optional[float] = None
    home_lon: Optional[float] = None
    notes: Optional[str] = ""
    tags: List[FlightTag] = []
    raw_path: List[GpsPoint] = []
    telemetry: List[TelemetrySample] = []


class FlightOut(FlightCreate):
    id: int
    owner_id: int
    mission_id: str
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FlightSummary(BaseModel):
    id: int
    mission_id: str
    drone_model: str
    date: datetime
    duration_sec: int
    distance_km: float
    max_alt_m: float
    batt_end_pct: int
    source: str
    tags: List[Any]

    model_config = {"from_attributes": True}


# ── Analytics ─────────────────────────────────────────────────────────────────

class OverviewStats(BaseModel):
    total_flights: int
    total_duration_hr: float
    total_distance_km: float
    max_alt_ever_m: float
    avg_duration_min: float
    avg_distance_km: float
    flights_by_drone: dict
    flights_by_month: dict


class BatteryHealthOut(BaseModel):
    serial: str
    label: str
    health_pct: float
    cycle_count: int
    avg_end_pct: float
    flights_count: int
