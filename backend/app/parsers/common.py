from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class ParsedGpsPoint:
    lat: float
    lon: float
    alt: float   # metres
    t: int       # seconds from start


@dataclass
class ParsedTelemetrySample:
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


@dataclass
class ParsedFlight:
    source: str
    drone_model: str
    battery_serial: str
    date: datetime
    duration_sec: int
    distance_km: float
    max_alt_m: float
    max_speed_ms: float
    batt_start_pct: int
    batt_end_pct: int
    home_lat: float
    home_lon: float
    tags: List[dict] = field(default_factory=list)
    path: List[ParsedGpsPoint] = field(default_factory=list)
    telemetry: List[ParsedTelemetrySample] = field(default_factory=list)


def auto_tag(flight: ParsedFlight) -> List[dict]:
    """Generate automatic tags based on flight characteristics."""
    tags = []
    hour = flight.date.hour
    if hour < 6 or hour >= 20:
        tags.append({"label": "NIGHT", "kind": "night"})
    if flight.max_speed_ms > 15:
        tags.append({"label": "HI-SPD", "kind": "speed"})
    if flight.batt_end_pct < 20:
        tags.append({"label": "LOW BATT", "kind": "warn"})
    if flight.max_alt_m > 120:
        tags.append({"label": "HIGH ALT", "kind": "warn"})
    return tags
