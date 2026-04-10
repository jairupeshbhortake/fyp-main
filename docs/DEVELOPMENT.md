# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional, for full-stack dev)

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/api/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173

The Vite dev proxy forwards `/api` requests to `http://localhost:8000`.

---

## Architecture

```
HTTP Request
    │
    ▼
Vue Router        ← frontend/src/router.js
    │
    ▼
View component    ← frontend/src/views/*.vue
    │ dispatch
    ▼
Vuex store        ← frontend/src/store/modules/
    │ axios
    ▼
FastAPI router    ← backend/app/routers/
    │
    ▼
SQLAlchemy ORM    ← backend/app/models.py
    │
    ▼
SQLite / PostgreSQL
```

---

## Adding a New API Endpoint

1. Add the route in the appropriate `backend/app/routers/*.py` file.
2. Add/update Pydantic schemas in `backend/app/schemas.py`.
3. Write a pytest test in `backend/tests/`.
4. Call the endpoint from `frontend/src/utils/api.js`.
5. Update `docs/API.md`.

---

## Adding a New Vue View

1. Create `frontend/src/views/MyView.vue`.
2. Register the route in `frontend/src/router.js`.
3. Add a `NavBar` link if needed.

---

## Testing

### Backend

```bash
cd backend
pytest -v
```

Tests live in `backend/tests/` (not scaffolded in this repo yet — contributions welcome).

### Frontend

```bash
cd frontend
npm run lint        # ESLint
```

---

## Database Migrations

The project uses `alembic` for migrations (configured but not yet initialised).

```bash
cd backend
alembic init migrations
# edit migrations/env.py to import Base from app.database
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

In development, `Base.metadata.create_all(bind=engine)` in `main.py` handles
schema creation automatically so migrations are optional during early development.

---

## Environment Variables

See `.env.example` for the full list. All backend settings are loaded via
`pydantic-settings` in `backend/app/database.py`.
