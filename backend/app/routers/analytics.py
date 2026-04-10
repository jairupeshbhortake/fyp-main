import io
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models, auth
from app.database import get_db
from app.analytics import compute_overview, detect_anomalies, compute_battery_health

router = APIRouter()


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flights = db.query(models.Flight).filter(
        models.Flight.owner_id == current_user.id
    ).all()
    return compute_overview(flights)


@router.get("/flights/{flight_id}/anomalies")
def flight_anomalies(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flight = db.query(models.Flight).filter(
        models.Flight.id == flight_id,
        models.Flight.owner_id == current_user.id,
    ).first()
    if not flight:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Flight not found")
    return detect_anomalies(flight.telemetry or [])


@router.get("/battery-health")
def battery_health(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flights = db.query(models.Flight).filter(
        models.Flight.owner_id == current_user.id
    ).all()
    return compute_battery_health(flights)


@router.get("/report/pdf")
def export_analytics_report_pdf(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flights = db.query(models.Flight).filter(
        models.Flight.owner_id == current_user.id
    ).all()
    overview = compute_overview(flights)

    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    can.setFont("Helvetica-Bold", 16)
    can.drawString(50, 800, "DroneVault Analytics Report")
    
    can.setFont("Helvetica", 12)
    y = 760
    
    lines = [
        f"Total Missions: {overview.get('total_flights', 0)}",
        f"Total Airtime (hr): {overview.get('total_duration_hr', 0)}",
        f"Total Range (km): {overview.get('total_distance_km', 0)}",
        f"Altitude Record (m): {overview.get('max_alt_ever_m', 0)}",
        f"Top Speed (m/s): {overview.get('max_speed_ever_ms', 0)}",
        f"Average Flight Time (min): {overview.get('avg_duration_min', 0)}",
        f"Average Distance (km): {overview.get('avg_distance_km', 0)}",
    ]
    
    for line in lines:
        can.drawString(50, y, line)
        y -= 20
        
    y -= 10
    can.setFont("Helvetica-Bold", 14)
    can.drawString(50, y, "Flights by Drone Model")
    can.setFont("Helvetica", 12)
    y -= 20
    for drone, count in overview.get("flights_by_drone", {}).items():
        can.drawString(70, y, f"- {drone}: {count}")
        y -= 20
        
    y -= 10
    can.setFont("Helvetica-Bold", 14)
    can.drawString(50, y, "Flights by Source")
    can.setFont("Helvetica", 12)
    y -= 20
    for src, count in overview.get("flights_by_source", {}).items():
        can.drawString(70, y, f"- {src}: {count}")
        y -= 20

    can.save()
    packet.seek(0)
    
    new_pdf = PdfReader(packet)
    output = PdfWriter()
    output.add_page(new_pdf.pages[0])
    
    out_stream = io.BytesIO()
    output.write(out_stream)
    out_stream.seek(0)

    return StreamingResponse(
        iter([out_stream.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="analytics_report.pdf"'}
    )
