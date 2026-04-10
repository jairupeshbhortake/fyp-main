from collections import defaultdict
from typing import List
from app.models import Flight


def compute_overview(flights: List[Flight]) -> dict:
    empty = {
        "total_flights": 0,
        "total_duration_hr": 0,
        "total_distance_km": 0,
        "max_alt_ever_m": 0,
        "max_speed_ever_ms": 0,
        "avg_duration_min": 0,
        "avg_distance_km": 0,
        "flights_by_drone": {},
        "flights_by_source": {},
        "flights_by_month": {},
        "flights_by_duration_bucket": {"Short (<10m)": 0, "Medium (10-25m)": 0, "Long (>25m)": 0},
        "flights_by_hour": {str(h): 0 for h in range(24)},
        "top_longest": [],
        "top_furthest": [],
        "home_locations": [],
    }
    if not flights:
        return empty

    total_dur_sec = sum(f.duration_sec or 0 for f in flights)
    total_dist    = sum(f.distance_km or 0 for f in flights)
    max_alt       = max(f.max_alt_m or 0 for f in flights)
    max_speed     = max(f.max_speed_ms or 0 for f in flights)

    by_drone: dict  = defaultdict(int)
    by_source: dict = defaultdict(int)
    by_month: dict  = defaultdict(int)
    by_dur: dict    = {"Short (<10m)": 0, "Medium (10-25m)": 0, "Long (>25m)": 0}
    by_hour: dict   = defaultdict(int)
    home_locs       = []

    for f in flights:
        by_drone[f.drone_model or "UNKNOWN"] += 1
        by_source[f.source or "UNKNOWN"] += 1

        if f.date:
            by_month[f.date.strftime("%Y-%m")] += 1
            by_hour[str(f.date.hour)] += 1

        dur_min = (f.duration_sec or 0) / 60
        if dur_min < 10:
            by_dur["Short (<10m)"] += 1
        elif dur_min <= 25:
            by_dur["Medium (10-25m)"] += 1
        else:
            by_dur["Long (>25m)"] += 1

        if f.home_lat and f.home_lon:
            home_locs.append({
                "lat": f.home_lat,
                "lon": f.home_lon,
                "mission_id": f.mission_id,
                "id": f.id,
            })

    # Fill zeros for missing hours
    hours_filled = {str(h): by_hour.get(str(h), 0) for h in range(24)}

    # Top 3 longest / furthest
    sorted_by_dur  = sorted(flights, key=lambda f: f.duration_sec or 0, reverse=True)
    sorted_by_dist = sorted(flights, key=lambda f: f.distance_km or 0, reverse=True)

    def flight_snippet(f):
        return {
            "id": f.id,
            "mission_id": f.mission_id,
            "date": f.date.isoformat() if f.date else None,
            "duration_sec": f.duration_sec,
            "distance_km": f.distance_km,
        }

    n = len(flights)
    return {
        "total_flights":              n,
        "total_duration_hr":          round(total_dur_sec / 3600, 2),
        "total_distance_km":          round(total_dist, 2),
        "max_alt_ever_m":             round(max_alt, 1),
        "max_speed_ever_ms":          round(max_speed, 1),
        "avg_duration_min":           round(total_dur_sec / n / 60, 1),
        "avg_distance_km":            round(total_dist / n, 2),
        "flights_by_drone":           dict(by_drone),
        "flights_by_source":          dict(by_source),
        "flights_by_month":           dict(sorted(by_month.items())),
        "flights_by_duration_bucket": by_dur,
        "flights_by_hour":            hours_filled,
        "top_longest":                [flight_snippet(f) for f in sorted_by_dur[:3]],
        "top_furthest":               [flight_snippet(f) for f in sorted_by_dist[:3]],
        "home_locations":             home_locs,
    }
