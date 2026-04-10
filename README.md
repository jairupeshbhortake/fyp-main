# DroneVault Analytics

> Full-stack drone flight log analytics platform — FastAPI backend · Vue 3 frontend · Docker deployment.

A privacy-first, self-hosted dashboard for organizing and analysing DJI and Litchi flight logs. Upload `.txt` (DJI decoded CSV) or `.csv` (Litchi export) files and instantly get telemetry charts, flight maps, battery health tracking, and anomaly detection.

---


https://github.com/user-attachments/assets/67050ea7-8372-4a8a-bc7c-7f1da05559a8



## Features

| Feature | Details |
|---|---|
| **Multi-format import** | DJI decoded CSV `.txt` and Litchi `.csv` with auto unit detection |
| **Interactive flight map** | SVG-projected GPS path with HUD overlay and replay |
| **Telemetry charts** | Altitude, speed, battery %, RC signal |
| **Battery health** | Per-serial cycle tracking with degradation model |
| **Anomaly detection** | Rule-based alerts for high altitude, low battery, weak signal |
| **Export** | CSV and GPX download per flight |
| **JWT auth** | Per-user data isolation, register + login |
| **Docker ready** | Single `docker compose up` for dev or prod |

## Tech Stack

**Backend** — Python 3.11 · FastAPI · SQLAlchemy · SQLite/PostgreSQL · JWT (python-jose)

**Frontend** — Vue 3 (Composition API) · Vuex 4 · Vue Router 4 · Canvas charts · SVG maps

**DevOps** — Docker · GitHub Actions CI/CD · GHCR image publishing

## Quick Start

### Option A — Docker (recommended)

```bash
git clone https://github.com/youruser/dronevault-analytics
cd dronevault-analytics
cp .env.example .env          # edit SECRET_KEY at minimum
docker compose up -d
```

Open [http://localhost:5173](http://localhost:5173), register an account, and import a flight log.

### Option B — Local development

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# API at http://localhost:8000 · Docs at http://localhost:8000/api/docs
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
# UI at http://localhost:5173
```

## Importing Flight Logs

| Log type | How to export |
|---|---|
| **DJI** | Use [AirData](https://airdata.com) or [CsvView](https://www.phantompilots.com/attachments/csvview-zip.99589/) to decode the binary `.txt` to CSV first |
| **Litchi** | Export from the Litchi app → `Flights` → `Export CSV` |

## Project Structure

```
skytraq-analytics/
├── backend/
│   └── app/
│       ├── main.py          # FastAPI app, CORS, router registration
│       ├── database.py      # SQLAlchemy engine + session + settings
│       ├── models.py        # ORM: User, Flight, Battery
│       ├── schemas.py       # Pydantic request/response models
│       ├── auth.py          # JWT creation + current_user dependency
│       ├── parsers/         # DJI + Litchi CSV parsers
│       ├── analytics/       # Stats, anomaly detection, battery health
│       └── routers/         # flights, auth, analytics, export
├── frontend/
│   └── src/
│       ├── views/           # Dashboard, FlightDetail, Analytics, BatteryHealth, Login
│       ├── components/      # dashboard/, maps/, charts/, common/
│       ├── store/           # Vuex modules: auth, flights, analytics
│       └── utils/           # api.js, helpers.js, constants.js
├── docker-compose.yml       # Dev stack
├── docker-compose.prod.yml  # Production stack
└── docs/                    # API, deployment, user guide, dev guide
```

## Running Tests

```bash
cd backend
pytest -q
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
