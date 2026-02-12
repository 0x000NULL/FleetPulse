"""Pydantic v2 models for FleetPulse API responses."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────
class VehicleStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    PARKED = "parked"
    OFFLINE = "offline"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"


# ── Vehicles ───────────────────────────────────────────────────
class VehiclePosition(BaseModel):
    latitude: float
    longitude: float
    bearing: float = 0
    speed: float = 0


class Vehicle(BaseModel):
    id: str
    name: str
    status: VehicleStatus = VehicleStatus.PARKED
    position: Optional[VehiclePosition] = None
    location_name: Optional[str] = None
    odometer_km: float = 0
    last_contact: Optional[datetime] = None


# ── Fleet Overview ─────────────────────────────────────────────
class FleetOverview(BaseModel):
    total_vehicles: int = 0
    active: int = 0
    idle: int = 0
    parked: int = 0
    offline: int = 0
    total_trips_today: int = 0
    total_distance_km: float = 0
    avg_trip_duration_min: float = 0
    avg_trip_distance_km: float = 0


class LocationStats(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    vehicle_count: int = 0
    active: int = 0
    safety_score: float = 100.0


# ── Safety ─────────────────────────────────────────────────────
class SafetyBreakdown(BaseModel):
    speeding: int = 0
    harsh_braking: int = 0
    harsh_acceleration: int = 0
    harsh_cornering: int = 0


class VehicleSafetyScore(BaseModel):
    vehicle_id: str
    vehicle_name: str
    score: float = Field(ge=0, le=100, default=100)
    breakdown: SafetyBreakdown = Field(default_factory=SafetyBreakdown)
    trend: TrendDirection = TrendDirection.STABLE
    event_count: int = 0


# ── Gamification ───────────────────────────────────────────────
class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon: str  # emoji
    earned: bool = False
    earned_at: Optional[datetime] = None


class DriverScore(BaseModel):
    driver_id: str
    driver_name: str
    points: int = 0
    safety_score: float = 100.0
    badges: list[Badge] = Field(default_factory=list)
    rank: int = 0


class Challenge(BaseModel):
    id: str
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    target_metric: str
    current_value: float = 0
    target_value: float = 0


class LocationRanking(BaseModel):
    location_name: str
    avg_safety_score: float
    total_points: int
    rank: int


# ── Alerts ─────────────────────────────────────────────────────
class Alert(BaseModel):
    id: str
    vehicle_id: str
    vehicle_name: str
    alert_type: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    acknowledged: bool = False


class AlertRule(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool = True
    threshold: Optional[float] = None
    alert_type: str
    severity: AlertSeverity = AlertSeverity.MEDIUM
