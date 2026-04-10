from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import flights, auth, analytics, export

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DroneVault Analytics API",
    description="Drone flight log analytics platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS – adjust origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(flights.router,   prefix="/api/flights",   tags=["Flights"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(export.router,    prefix="/api/export",    tags=["Export"])


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "dronevault-analytics"}
