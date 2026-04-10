"""
Battery health computation.
Groups flights by battery serial and calculates health metrics.
"""

from collections import defaultdict
from typing import List
from app.models import Flight


def compute_battery_health(flights: List[Flight]) -> List[dict]:
    """
    For each unique battery serial, compute:
    - cycle count (number of flights)
    - average end battery %
    - estimated health % (degrades with cycles and low-end usage)
    """
    groups: dict[str, list[Flight]] = defaultdict(list)
    for f in flights:
        serial = f.battery_serial or "UNKNOWN"
        groups[serial].append(f)

    results = []
    for serial, flist in groups.items():
        cycle_count = len(flist)
        avg_end_pct = sum(f.batt_end_pct or 0 for f in flist) / cycle_count

        # Simple health model:
        # - Start at 100%, lose ~0.1% per cycle
        # - Extra penalty for consistently draining below 20%
        deep_discharge_count = sum(1 for f in flist if (f.batt_end_pct or 100) < 20)
        health_pct = max(60.0, 100.0 - (cycle_count * 0.1) - (deep_discharge_count * 0.5))

        results.append({
            "serial":       serial,
            "label":        serial,
            "health_pct":   round(health_pct, 1),
            "cycle_count":  cycle_count,
            "avg_end_pct":  round(avg_end_pct, 1),
            "flights_count": cycle_count,
        })

    return sorted(results, key=lambda r: r["health_pct"])
