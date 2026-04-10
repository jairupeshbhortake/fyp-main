# API Reference

Base URL: `http://localhost:8000` (dev) or your production domain.

Interactive docs available at `/api/docs` (Swagger UI) and `/api/redoc`.

---

## Authentication

All endpoints except `/api/auth/register` and `/api/auth/token` require a
Bearer token in the `Authorization` header.

```
Authorization: Bearer <access_token>
```

### POST /api/auth/register

Create a new user account.

**Request body**
```json
{ "email": "pilot@example.com", "username": "mavic_pilot", "password": "secret" }
```

**Response 201**
```json
{ "id": 1, "email": "pilot@example.com", "username": "mavic_pilot", "is_active": true, "created_at": "..." }
```

---

### POST /api/auth/token

Obtain a JWT access token (OAuth2 password flow).

**Form data**: `username`, `password`

**Response 200**
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

---

## Flights

### GET /api/flights/

List flights for the authenticated user.

**Query params**

| Param | Type | Description |
|-------|------|-------------|
| `drone` | string | Filter by drone model |
| `date_from` | ISO date | Start of date range |
| `date_to` | ISO date | End of date range |
| `limit` | int (≤500) | Page size (default 100) |
| `offset` | int | Page offset |

**Response 200** — array of `FlightSummary`

---

### GET /api/flights/{id}

Get full flight detail including `raw_path` and `telemetry`.

**Response 200** — `FlightOut`

---

### POST /api/flights/

Create a manual flight entry.

**Request body** — `FlightCreate`

**Response 201** — `FlightOut`

---

### POST /api/flights/upload

Upload a DJI `.txt` or Litchi `.csv` log file.

**Form data**: `file` (multipart)

**Response 201** — `FlightOut`

---

### DELETE /api/flights/{id}

Delete a flight. Returns 204 No Content.

---

## Analytics

### GET /api/analytics/overview

Aggregate stats for all user flights.

**Response 200**
```json
{
  "total_flights": 37,
  "total_duration_hr": 14.3,
  "total_distance_km": 128.6,
  "max_alt_ever_m": 312.0,
  "avg_duration_min": 23.2,
  "avg_distance_km": 3.47,
  "flights_by_drone": { "MAVIC-3-PRO": 22, "MINI-4-PRO": 15 },
  "flights_by_month": { "2024-01": 3, "2024-02": 8 }
}
```

---

### GET /api/analytics/anomalies/{flight_id}

Rule-based anomaly events for a flight's telemetry.

**Response 200** — array of `{ t, field, value, level, msg }`

---

### GET /api/analytics/battery-health

Per-battery health metrics.

**Response 200** — array of `BatteryHealthOut`

---

## Export

### GET /api/export/csv/{flight_id}

Download flight telemetry as CSV.

### GET /api/export/gpx/{flight_id}

Download flight path as GPX.

### GET /api/export/kml/{flight_id}

Download flight path as KML.
