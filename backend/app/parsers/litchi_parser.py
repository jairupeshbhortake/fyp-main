"""
Litchi CSV export parser.

Litchi exports a CSV where headers indicate units, e.g.:
  datetime(utc), latitude, longitude, altitude(m) or altitude(feet),
  speed(m/s) or speed(mph), isPhoto, isVideo, rc_channels, ...

The parser auto-detects metric vs imperial units from the header names
and converts everything to metric internally.
"""

import io
import csv
import math
from datetime import datetime
from typing import IO

from app.parsers.common import (
    ParsedFlight, ParsedGpsPoint, ParsedTelemetrySample, auto_tag
)

FT_TO_M  = 0.3048
MPH_TO_MS = 0.44704


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def _find_col(headers: list[str], *candidates: str) -> str | None:
    for c in candidates:
        for h in headers:
            if c.lower() in h.lower():
                return h
    return None


def parse_litchi_csv(file: IO[bytes]) -> ParsedFlight:
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(content))
    headers = reader.fieldnames or []
    rows = list(reader)

    if not rows:
        raise ValueError("Empty Litchi CSV file")

    # Unit detection
    alt_col   = _find_col(headers, "altitude(m)", "altitude(feet)", "altitude")
    speed_col = _find_col(headers, "speed(m/s)", "speed(mph)", "speed")
    lat_col   = _find_col(headers, "latitude")
    lon_col   = _find_col(headers, "longitude")
    dt_col    = _find_col(headers, "datetime(utc)", "datetime", "time")

    imperial_alt   = alt_col   and "feet" in (alt_col or "").lower()
    imperial_speed = speed_col and "mph"  in (speed_col or "").lower()

    path: list[ParsedGpsPoint] = []
    telemetry: list[ParsedTelemetrySample] = []
    start_dt: datetime | None = None
    home_lat = home_lon = 0.0
    total_dist = 0.0
    prev_lat = prev_lon = None

    for row in rows:
        try:
            lat   = float(row.get(lat_col, 0) or 0)
            lon   = float(row.get(lon_col, 0) or 0)
            alt   = float(row.get(alt_col, 0) or 0)
            speed = float(row.get(speed_col, 0) or 0)

            if imperial_alt:   alt   *= FT_TO_M
            if imperial_speed: speed *= MPH_TO_MS

            dt_str = row.get(dt_col, "").strip()
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00")) if dt_str else datetime.utcnow()

            if start_dt is None:
                start_dt = dt
                home_lat, home_lon = lat, lon

            t_sec = int((dt - start_dt).total_seconds())

            if prev_lat is not None:
                total_dist += _haversine(prev_lat, prev_lon, lat, lon)
            prev_lat, prev_lon = lat, lon

            path.append(ParsedGpsPoint(lat=lat, lon=lon, alt=alt, t=t_sec))
            telemetry.append(ParsedTelemetrySample(
                t=t_sec, alt_m=alt, speed_ms=speed, batt_pct=80.0,
                rc_signal=85.0, video_signal=90.0, gps_signal=80.0,
                heading_deg=0.0, dist_home_m=_haversine(home_lat, home_lon, lat, lon) * 1000,
                temp_c=28.0,
            ))
        except Exception:
            continue

    if not path:
        raise ValueError("No valid GPS data in Litchi CSV")

    duration = path[-1].t
    flight = ParsedFlight(
        source="LITCHI",
        drone_model="DJI UNKNOWN",
        battery_serial="BT-LITCHI-UNKNOWN",
        date=start_dt or datetime.utcnow(),
        duration_sec=duration,
        distance_km=round(total_dist, 2),
        max_alt_m=round(max(p.alt for p in path), 1),
        max_speed_ms=round(max(s.speed_ms for s in telemetry), 1),
        batt_start_pct=100,
        batt_end_pct=int(telemetry[-1].batt_pct) if telemetry else 0,
        home_lat=home_lat,
        home_lon=home_lon,
        path=path,
        telemetry=telemetry,
    )
    flight.tags = [{"label": "LITCHI", "kind": "ok"}, *auto_tag(flight)]
    return flight
