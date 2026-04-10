"""
DJI .txt log parser.

DJI flight logs are binary-encoded. This module provides a lightweight
CSV-mode parser for DJI logs that have already been decoded (e.g. via
the dji-log-parser CLI or the AirData export). It expects a UTF-8 CSV
with at minimum the following columns (case-insensitive):

  datetime, latitude, longitude, altitude(m), speed(m/s),
  battery_percent, distance(m), rc_signal(%), video_signal(%),
  compass_heading(°)

If you need raw binary .txt parsing, integrate the dji-log-parser WASM
library on the frontend or call its CLI in a subprocess here.
"""

import io
import csv
import math
from datetime import datetime
from typing import IO

from app.parsers.common import (
    ParsedFlight, ParsedGpsPoint, ParsedTelemetrySample, auto_tag
)


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in km between two GPS coords."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_dji_txt(file: IO[bytes]) -> ParsedFlight:
    """Parse a decoded DJI CSV log file and return a ParsedFlight."""
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        raise ValueError("Empty DJI log file")

    # Normalise keys
    def _key(row: dict, *candidates: str) -> float:
        for c in candidates:
            for k in row:
                if k.strip().lower().startswith(c.lower()):
                    try:
                        return float(row[k])
                    except (ValueError, TypeError):
                        pass
        return 0.0

    path: list[ParsedGpsPoint] = []
    telemetry: list[ParsedTelemetrySample] = []
    start_dt: datetime | None = None
    home_lat = home_lon = 0.0
    total_dist = 0.0
    prev_lat = prev_lon = None

    for i, row in enumerate(rows):
        try:
            lat = _key(row, "latitude")
            lon = _key(row, "longitude")
            alt = _key(row, "altitude")
            speed = _key(row, "speed")
            batt = _key(row, "battery")
            heading = _key(row, "compass", "heading")
            dist_home = _key(row, "distance")
            rc = _key(row, "rc_signal", "rc signal")
            video = _key(row, "video_signal", "video signal")

            # Parse timestamp
            dt_str = ""
            for k in row:
                if "datetime" in k.lower() or "time" in k.lower():
                    dt_str = row[k].strip()
                    break
            dt = datetime.fromisoformat(dt_str) if dt_str else datetime.utcnow()

            if start_dt is None:
                start_dt = dt
                home_lat, home_lon = lat, lon

            t_sec = int((dt - start_dt).total_seconds())

            if prev_lat is not None:
                total_dist += _haversine(prev_lat, prev_lon, lat, lon)
            prev_lat, prev_lon = lat, lon

            path.append(ParsedGpsPoint(lat=lat, lon=lon, alt=alt, t=t_sec))
            telemetry.append(ParsedTelemetrySample(
                t=t_sec, alt_m=alt, speed_ms=speed, batt_pct=batt,
                rc_signal=rc or 85.0, video_signal=video or 90.0,
                gps_signal=80.0, heading_deg=heading,
                dist_home_m=dist_home, temp_c=28.0,
            ))
        except Exception:
            continue

    if not path:
        raise ValueError("No valid GPS data found in DJI log")

    duration = path[-1].t if path else 0
    max_alt = max(p.alt for p in path)
    max_speed = max(s.speed_ms for s in telemetry)
    batt_start = int(telemetry[0].batt_pct) if telemetry else 100
    batt_end = int(telemetry[-1].batt_pct) if telemetry else 0

    flight = ParsedFlight(
        source="DJI",
        drone_model="DJI UNKNOWN",
        battery_serial="BT-DJI-UNKNOWN",
        date=start_dt or datetime.utcnow(),
        duration_sec=duration,
        distance_km=round(total_dist, 2),
        max_alt_m=round(max_alt, 1),
        max_speed_ms=round(max_speed, 1),
        batt_start_pct=batt_start,
        batt_end_pct=batt_end,
        home_lat=home_lat,
        home_lon=home_lon,
        path=path,
        telemetry=telemetry,
    )
    flight.tags = auto_tag(flight)
    return flight
