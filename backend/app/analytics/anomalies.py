"""
Simple rule-based anomaly detector.
Flags any telemetry sample that exceeds configurable thresholds.
"""

from typing import Any


THRESHOLDS = {
    "alt_m":      {"warn": 100,  "critical": 150},
    "speed_ms":   {"warn": 15,   "critical": 20},
    "batt_pct":   {"warn": 25,   "critical": 15},   # lower is worse
    "temp_c":     {"warn": 40,   "critical": 50},
    "rc_signal":  {"warn": 50,   "critical": 30},   # lower is worse
}


def detect_anomalies(telemetry: list[dict[str, Any]]) -> list[dict]:
    """Return a list of anomaly events found in telemetry samples."""
    events = []

    for sample in telemetry:
        t = sample.get("t", 0)

        # Altitude
        alt = sample.get("alt_m", 0)
        if alt >= THRESHOLDS["alt_m"]["critical"]:
            events.append({"t": t, "field": "alt_m", "value": alt, "level": "critical", "msg": f"Critical altitude {alt:.0f}m"})
        elif alt >= THRESHOLDS["alt_m"]["warn"]:
            events.append({"t": t, "field": "alt_m", "value": alt, "level": "warn", "msg": f"High altitude {alt:.0f}m"})

        # Speed
        spd = sample.get("speed_ms", 0)
        if spd >= THRESHOLDS["speed_ms"]["critical"]:
            events.append({"t": t, "field": "speed_ms", "value": spd, "level": "critical", "msg": f"Critical speed {spd:.1f}m/s"})
        elif spd >= THRESHOLDS["speed_ms"]["warn"]:
            events.append({"t": t, "field": "speed_ms", "value": spd, "level": "warn", "msg": f"High speed {spd:.1f}m/s"})

        # Battery (inverted – low is bad)
        batt = sample.get("batt_pct", 100)
        if batt <= THRESHOLDS["batt_pct"]["critical"]:
            events.append({"t": t, "field": "batt_pct", "value": batt, "level": "critical", "msg": f"Critical battery {batt:.0f}%"})
        elif batt <= THRESHOLDS["batt_pct"]["warn"]:
            events.append({"t": t, "field": "batt_pct", "value": batt, "level": "warn", "msg": f"Low battery {batt:.0f}%"})

        # Temperature
        temp = sample.get("temp_c", 0)
        if temp >= THRESHOLDS["temp_c"]["critical"]:
            events.append({"t": t, "field": "temp_c", "value": temp, "level": "critical", "msg": f"Critical temp {temp:.0f}°C"})
        elif temp >= THRESHOLDS["temp_c"]["warn"]:
            events.append({"t": t, "field": "temp_c", "value": temp, "level": "warn", "msg": f"High temp {temp:.0f}°C"})

        # RC signal (inverted)
        rc = sample.get("rc_signal", 100)
        if rc <= THRESHOLDS["rc_signal"]["critical"]:
            events.append({"t": t, "field": "rc_signal", "value": rc, "level": "critical", "msg": f"Critical RC signal {rc:.0f}%"})
        elif rc <= THRESHOLDS["rc_signal"]["warn"]:
            events.append({"t": t, "field": "rc_signal", "value": rc, "level": "warn", "msg": f"Weak RC signal {rc:.0f}%"})

    # Deduplicate consecutive same-field events (keep first occurrence per 30s window)
    seen: dict[str, int] = {}
    deduped = []
    for ev in events:
        last = seen.get(ev["field"], -999)
        if ev["t"] - last >= 30:
            deduped.append(ev)
            seen[ev["field"]] = ev["t"]

    return deduped
