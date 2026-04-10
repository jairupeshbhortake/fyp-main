from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, JSON, String, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String, unique=True, index=True, nullable=False)
    username   = Column(String, unique=True, index=True, nullable=False)
    hashed_pw  = Column(String, nullable=False)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    flights    = relationship("Flight", back_populates="owner", cascade="all, delete")
    batteries  = relationship("Battery", back_populates="owner", cascade="all, delete")


class Flight(Base):
    __tablename__ = "flights"

    id              = Column(Integer, primary_key=True, index=True)
    owner_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    mission_id      = Column(String, unique=True, index=True)
    source          = Column(String)           # DJI | LITCHI | MANUAL
    drone_model     = Column(String)
    battery_serial  = Column(String, index=True)
    date            = Column(DateTime, index=True)
    duration_sec    = Column(Integer)
    distance_km     = Column(Float)
    max_alt_m       = Column(Float)
    max_speed_ms    = Column(Float)
    batt_start_pct  = Column(Integer)
    batt_end_pct    = Column(Integer)
    home_lat        = Column(Float)
    home_lon        = Column(Float)
    tags            = Column(JSON, default=list)
    raw_path        = Column(JSON, default=list)   # [{lat, lon, alt, t}]
    telemetry       = Column(JSON, default=list)   # [{t, alt, speed, batt, ...}]
    notes           = Column(Text, default="")
    created_at      = Column(DateTime, default=datetime.utcnow)

    owner           = relationship("User", back_populates="flights")


class Battery(Base):
    __tablename__ = "batteries"

    id          = Column(Integer, primary_key=True, index=True)
    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    serial      = Column(String, index=True)
    label       = Column(String, default="")
    capacity_mah = Column(Integer, default=0)
    cycle_count = Column(Integer, default=0)
    health_pct  = Column(Float, default=100.0)
    created_at  = Column(DateTime, default=datetime.utcnow)

    owner       = relationship("User", back_populates="batteries")
