import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db
from app.parsers import parse_dji_txt, parse_litchi_csv

router = APIRouter()


def _mission_id() -> str:
    return f"MSN-{uuid.uuid4().hex[:8].upper()}"


@router.get("", response_model=List[schemas.FlightSummary])
def list_flights(
    drone:    Optional[str] = Query(None),
    source:   Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to:   Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    q = db.query(models.Flight).filter(models.Flight.owner_id == current_user.id)
    if drone:
        q = q.filter(models.Flight.drone_model == drone)
    if source:
        q = q.filter(models.Flight.source == source)
    if date_from:
        q = q.filter(models.Flight.date >= date_from)
    if date_to:
        q = q.filter(models.Flight.date <= date_to)
    return q.order_by(models.Flight.date.desc()).offset(skip).limit(limit).all()


@router.get("/{flight_id}", response_model=schemas.FlightOut)
def get_flight(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flight = db.query(models.Flight).filter(
        models.Flight.id == flight_id,
        models.Flight.owner_id == current_user.id,
    ).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


@router.post("", response_model=schemas.FlightOut, status_code=201)
def create_flight(
    payload: schemas.FlightCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flight = models.Flight(
        owner_id=current_user.id,
        mission_id=_mission_id(),
        source="MANUAL",
        **payload.model_dump(),
    )
    db.add(flight)
    db.commit()
    db.refresh(flight)
    return flight


@router.post("/upload", response_model=schemas.FlightOut, status_code=201)
async def upload_flight_log(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    filename = (file.filename or "").lower()
    try:
        if filename.endswith(".csv"):
            parsed = parse_litchi_csv(file.file)
        elif filename.endswith(".txt"):
            parsed = parse_dji_txt(file.file)
        else:
            raise HTTPException(status_code=422, detail="Unsupported file type. Upload .txt or .csv")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    flight = models.Flight(
        owner_id=current_user.id,
        mission_id=_mission_id(),
        source=parsed.source,
        drone_model=parsed.drone_model,
        battery_serial=parsed.battery_serial,
        date=parsed.date,
        duration_sec=parsed.duration_sec,
        distance_km=parsed.distance_km,
        max_alt_m=parsed.max_alt_m,
        max_speed_ms=parsed.max_speed_ms,
        batt_start_pct=parsed.batt_start_pct,
        batt_end_pct=parsed.batt_end_pct,
        home_lat=parsed.home_lat,
        home_lon=parsed.home_lon,
        tags=[t.__dict__ if hasattr(t, "__dict__") else t for t in parsed.tags],
        raw_path=[p.__dict__ for p in parsed.path],
        telemetry=[t.__dict__ for t in parsed.telemetry],
    )
    db.add(flight)
    db.commit()
    db.refresh(flight)
    return flight


@router.delete("/{flight_id}", status_code=204)
def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flight = db.query(models.Flight).filter(
        models.Flight.id == flight_id,
        models.Flight.owner_id == current_user.id,
    ).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    db.delete(flight)
    db.commit()


@router.delete("", status_code=204)
def delete_all_flights(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db.query(models.Flight).filter(models.Flight.owner_id == current_user.id).delete()
    db.commit()
