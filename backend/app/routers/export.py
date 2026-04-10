import csv
import io
import math
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models, auth
from app.database import get_db

router = APIRouter()


def _get_flight_or_404(flight_id: int, user: models.User, db: Session) -> models.Flight:
    flight = db.query(models.Flight).filter(
        models.Flight.id == flight_id,
        models.Flight.owner_id == user.id,
    ).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


@router.get("/{flight_id}/csv")
def export_csv(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flight = _get_flight_or_404(flight_id, current_user, db)
    telemetry = flight.telemetry or []

    buf = io.StringIO()
    if telemetry:
        writer = csv.DictWriter(buf, fieldnames=list(telemetry[0].keys()))
        writer.writeheader()
        writer.writerows(telemetry)

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{flight.mission_id}.csv"'},
    )


@router.get("/{flight_id}/gpx")
def export_gpx(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flight = _get_flight_or_404(flight_id, current_user, db)
    path = flight.raw_path or []

    pts = "\n".join(
        f'    <trkpt lat="{p["lat"]:.6f}" lon="{p["lon"]:.6f}">'
        f'<ele>{p["alt"]:.1f}</ele></trkpt>'
        for p in path
    )
    gpx = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="DroneVault Analytics">
  <trk>
    <name>{flight.mission_id}</name>
    <trkseg>
{pts}
    </trkseg>
  </trk>
</gpx>"""

    return StreamingResponse(
        iter([gpx]),
        media_type="application/gpx+xml",
        headers={"Content-Disposition": f'attachment; filename="{flight.mission_id}.gpx"'},
    )


@router.get("/{flight_id}/kml")
def export_kml(
    flight_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    flight = _get_flight_or_404(flight_id, current_user, db)
    path = flight.raw_path or []

    coords = "\n".join(
        f"{p['lon']:.6f},{p['lat']:.6f},{p['alt']:.1f}" for p in path
    )
    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{flight.mission_id}</name>
    <Placemark>
      <name>{flight.mission_id}</name>
      <LineString>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>{coords}</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>"""

    return StreamingResponse(
        iter([kml]),
        media_type="application/vnd.google-earth.kml+xml",
        headers={"Content-Disposition": f'attachment; filename="{flight.mission_id}.kml"'},
    )
