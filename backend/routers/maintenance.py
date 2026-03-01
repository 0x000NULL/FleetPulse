"""Predictive maintenance endpoints – optimized with caching and timeouts."""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException

from _cache import get_cached, set_cached
from geotab_client import GeotabClient
from models import (
    MaintenancePrediction,
    VehicleMaintenanceDetail,
    MaintenanceCost,
    UrgentMaintenanceAlert,
    MaintenanceType,
    UrgencyLevel,
)

logger = logging.getLogger(__name__)
router = APIRouter()

MAINTENANCE_INTERVALS = {
    "oil_change": {"miles": 5000, "months": 6},
    "brake_service": {"miles": 30000, "months": 24},
    "tire_rotation": {"miles": 7500, "months": 12},
    "transmission_service": {"miles": 60000, "months": 48},
}

MAINTENANCE_COSTS = {
    "oil_change": 75,
    "brake_service": 600,
    "tire_rotation": 25,
    "transmission_service": 300,
    "tires_replacement": 600,
}


def _get_devices_cached() -> list[dict]:
    cached = get_cached("maint:devices", ttl=300)
    if cached is not None:
        return cached
    try:
        devices = GeotabClient.get().get_devices()
        set_cached("maint:devices", devices)
        return devices
    except (TimeoutError, Exception) as e:
        logger.warning(f"Failed to fetch devices for maintenance: {e}")
        return []


def calculate_maintenance_due_date(last_service: datetime, odometer_at_service: float,
                                   current_odometer: float, service_type: str) -> tuple[datetime, bool]:
    intervals = MAINTENANCE_INTERVALS[service_type]
    miles_since_service = current_odometer - odometer_at_service
    miles_remaining = intervals["miles"] - miles_since_service
    avg_miles_per_day = 50
    days_until_due = max(0, miles_remaining / avg_miles_per_day)
    due_date_by_miles = datetime.now(timezone.utc) + timedelta(days=days_until_due)
    due_date_by_time = last_service + timedelta(days=intervals["months"] * 30)
    due_date = min(due_date_by_miles, due_date_by_time)
    is_overdue = due_date < datetime.now(timezone.utc)
    return due_date, is_overdue


def get_urgency_level(due_date: datetime, has_fault_codes: bool = False) -> UrgencyLevel:
    if has_fault_codes:
        return UrgencyLevel.CRITICAL
    days_until_due = (due_date - datetime.now(timezone.utc)).days
    if days_until_due < 0:
        return UrgencyLevel.CRITICAL
    elif days_until_due <= 7:
        return UrgencyLevel.HIGH
    elif days_until_due <= 30:
        return UrgencyLevel.MEDIUM
    return UrgencyLevel.LOW


def _get_fleet_odometers() -> dict[str, float]:
    """Get odometer readings for all devices in ONE API call."""
    cached = get_cached("maint:odometers", ttl=300)
    if cached is not None:
        return cached
    try:
        client = GeotabClient.get()
        data = client.get_status_data(
            diagnostic_id="DiagnosticOdometerId",
            from_date=datetime.now(timezone.utc) - timedelta(days=1),
        )
        result: dict[str, float] = {}
        for d in data:
            dev_id = d.get("device", {}).get("id", "")
            if dev_id:
                result[dev_id] = float(d.get("data", 0)) * 0.621371
        set_cached("maint:odometers", result)
        return result
    except (TimeoutError, Exception) as e:
        logger.warning(f"Failed to fetch odometers: {e}")
        return {}


def _get_fleet_engine_hours() -> dict[str, float]:
    cached = get_cached("maint:engine_hours", ttl=300)
    if cached is not None:
        return cached
    try:
        client = GeotabClient.get()
        data = client.get_status_data(
            diagnostic_id="DiagnosticEngineHoursId",
            from_date=datetime.now(timezone.utc) - timedelta(days=1),
        )
        result: dict[str, float] = {}
        for d in data:
            dev_id = d.get("device", {}).get("id", "")
            if dev_id:
                result[dev_id] = float(d.get("data", 0))
        set_cached("maint:engine_hours", result)
        return result
    except (TimeoutError, Exception) as e:
        logger.warning(f"Failed to fetch engine hours: {e}")
        return {}


def _get_fleet_faults() -> dict[str, list[dict]]:
    """Get fault data for ALL devices in ONE API call."""
    cached = get_cached("maint:faults", ttl=300)
    if cached is not None:
        return cached
    try:
        client = GeotabClient.get()
        fault_data = client._call(
            client.api.get, "FaultData",
            search={"fromDate": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()},
        )
        result: dict[str, list[dict]] = {}
        for f in fault_data:
            dev_id = f.get("device", {}).get("id", "")
            if dev_id:
                result.setdefault(dev_id, []).append(f)
        set_cached("maint:faults", result)
        return result
    except (TimeoutError, Exception) as e:
        logger.warning(f"Failed to fetch faults: {e}")
        return {}


@router.get("/predictions", response_model=List[MaintenancePrediction])
async def get_maintenance_predictions():
    cached = get_cached("maintenance_predictions", ttl=300)
    if cached is not None:
        return cached
    try:
        devices = _get_devices_cached()
        odometers = _get_fleet_odometers()
        engine_hours_map = _get_fleet_engine_hours()
        faults_map = _get_fleet_faults()

        predictions = []
        now = datetime.now(timezone.utc)

        for device in devices:
            device_id = device.get("id", "")
            device_name = device.get("name", "Unknown Vehicle")
            current_odometer = odometers.get(device_id, 0)
            engine_hours = engine_hours_map.get(device_id, 0)
            device_faults = faults_map.get(device_id, [])
            has_fault_codes = len(device_faults) > 0
            active_fault_count = len([f for f in device_faults if not f.get("dismissDateTime")])

            base_date = now - timedelta(days=90)
            base_odometer = max(0, current_odometer - 3000)

            upcoming_services = []
            for service_type in MAINTENANCE_INTERVALS:
                due_date, is_overdue = calculate_maintenance_due_date(
                    base_date, base_odometer, current_odometer, service_type
                )
                urgency = get_urgency_level(due_date, has_fault_codes)
                upcoming_services.append({
                    "service_type": service_type,
                    "due_date": due_date,
                    "is_overdue": is_overdue,
                    "urgency": urgency,
                    "estimated_cost": MAINTENANCE_COSTS[service_type],
                })

            predictions.append(MaintenancePrediction(
                vehicle_id=device_id, vehicle_name=device_name,
                current_odometer=current_odometer, engine_hours=engine_hours,
                upcoming_services=upcoming_services,
                has_active_fault_codes=has_fault_codes,
                active_fault_count=active_fault_count,
            ))

        set_cached("maintenance_predictions", predictions)
        return predictions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get maintenance predictions: {str(e)}")


@router.get("/vehicle/{vehicle_id}", response_model=VehicleMaintenanceDetail)
async def get_vehicle_maintenance_detail(vehicle_id: str):
    cached = get_cached(f"maint:vehicle:{vehicle_id}", ttl=300)
    if cached is not None:
        return cached
    try:
        devices = _get_devices_cached()
        device = next((d for d in devices if d.get("id") == vehicle_id), None)
        if not device:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        device_name = device.get("name", "Unknown Vehicle")
        odometers = _get_fleet_odometers()
        engine_hours_map = _get_fleet_engine_hours()
        faults_map = _get_fleet_faults()

        current_odometer = odometers.get(vehicle_id, 0)
        engine_hours = engine_hours_map.get(vehicle_id, 0)
        device_faults = faults_map.get(vehicle_id, [])

        active_faults = []
        for fault in device_faults:
            if not fault.get("dismissDateTime"):
                active_faults.append({
                    "code": fault.get("diagnostic", {}).get("code", "Unknown"),
                    "description": fault.get("diagnostic", {}).get("name", "Unknown Fault"),
                    "timestamp": fault.get("dateTime", datetime.now(timezone.utc)),
                    "severity": "high",
                })

        now = datetime.now(timezone.utc)
        base_date = now - timedelta(days=90)
        base_odometer = max(0, current_odometer - 3000)

        maintenance_history = []
        for i, service_type in enumerate(MAINTENANCE_INTERVALS):
            past_date = now - timedelta(days=90 + i * 30)
            maintenance_history.append({
                "service_type": service_type,
                "date": past_date,
                "odometer_at_service": max(0, current_odometer - (3000 - i * 500)),
                "cost": MAINTENANCE_COSTS[service_type],
                "notes": f"Completed {service_type.replace('_', ' ')} service",
            })

        upcoming_services = []
        for service_type in MAINTENANCE_INTERVALS:
            due_date, is_overdue = calculate_maintenance_due_date(
                base_date, base_odometer, current_odometer, service_type
            )
            urgency = get_urgency_level(due_date, len(active_faults) > 0)
            upcoming_services.append({
                "service_type": service_type, "due_date": due_date,
                "is_overdue": is_overdue, "urgency": urgency,
                "estimated_cost": MAINTENANCE_COSTS[service_type],
            })

        result = VehicleMaintenanceDetail(
            vehicle_id=vehicle_id, vehicle_name=device_name,
            current_odometer=current_odometer, engine_hours=engine_hours,
            upcoming_services=upcoming_services,
            maintenance_history=maintenance_history,
            active_fault_codes=active_faults,
            last_service_date=base_date,
        )
        set_cached(f"maint:vehicle:{vehicle_id}", result)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vehicle maintenance detail: {str(e)}")


@router.get("/costs", response_model=MaintenanceCost)
async def get_maintenance_costs():
    cached = get_cached("maintenance_costs", ttl=300)
    if cached is not None:
        return cached
    try:
        devices = _get_devices_cached()
        now = datetime.now(timezone.utc)
        next_month = now + timedelta(days=30)
        next_3_months = now + timedelta(days=90)

        total_cost_next_month = 0
        total_cost_next_3_months = 0
        cost_breakdown: dict[str, dict] = {}

        for device in devices:
            current_odometer = 15000
            base_date = now - timedelta(days=90)
            base_odometer = current_odometer - 3000

            for service_type in MAINTENANCE_INTERVALS:
                due_date, _ = calculate_maintenance_due_date(
                    base_date, base_odometer, current_odometer, service_type
                )
                cost = MAINTENANCE_COSTS[service_type]
                if due_date <= next_month:
                    total_cost_next_month += cost
                    if service_type not in cost_breakdown:
                        cost_breakdown[service_type] = {"count": 0, "total_cost": 0}
                    cost_breakdown[service_type]["count"] += 1
                    cost_breakdown[service_type]["total_cost"] += cost
                if due_date <= next_3_months:
                    total_cost_next_3_months += cost

        result = MaintenanceCost(
            total_cost_next_month=total_cost_next_month,
            total_cost_next_3_months=total_cost_next_3_months,
            cost_breakdown=cost_breakdown,
            average_monthly_cost=total_cost_next_3_months / 3,
        )
        set_cached("maintenance_costs", result)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get maintenance costs: {str(e)}")


@router.get("/urgent", response_model=List[UrgentMaintenanceAlert])
async def get_urgent_maintenance():
    cached = get_cached("maintenance_urgent", ttl=300)
    if cached is not None:
        return cached
    try:
        devices = _get_devices_cached()
        faults_map = _get_fleet_faults()
        urgent_alerts = []
        now = datetime.now(timezone.utc)

        for device in devices:
            device_id = device.get("id", "")
            device_name = device.get("name", "Unknown Vehicle")
            active_faults = [f for f in faults_map.get(device_id, []) if not f.get("dismissDateTime")]

            current_odometer = 15000
            base_date = now - timedelta(days=90)
            base_odometer = current_odometer - 3000

            overdue_services = []
            urgent_services = []

            for service_type in MAINTENANCE_INTERVALS:
                due_date, is_overdue = calculate_maintenance_due_date(
                    base_date, base_odometer, current_odometer, service_type
                )
                if is_overdue:
                    overdue_services.append({
                        "service_type": service_type, "due_date": due_date,
                        "days_overdue": (now - due_date).days,
                    })
                elif (due_date - now).days <= 7:
                    urgent_services.append({
                        "service_type": service_type, "due_date": due_date,
                        "days_until_due": (due_date - now).days,
                    })

            if active_faults or overdue_services or urgent_services:
                urgency = UrgencyLevel.CRITICAL if (active_faults or overdue_services) else UrgencyLevel.HIGH
                alert = UrgentMaintenanceAlert(
                    vehicle_id=device_id, vehicle_name=device_name,
                    urgency=urgency,
                    active_fault_codes=[{
                        "code": f.get("diagnostic", {}).get("code", "Unknown"),
                        "description": f.get("diagnostic", {}).get("name", "Unknown Fault"),
                    } for f in active_faults],
                    overdue_services=overdue_services,
                    urgent_services=urgent_services,
                    estimated_repair_cost=sum(
                        MAINTENANCE_COSTS.get(s["service_type"], 0)
                        for s in overdue_services + urgent_services
                    ),
                )
                urgent_alerts.append(alert)

        urgent_alerts.sort(key=lambda x: (x.urgency.value, x.vehicle_name))
        set_cached("maintenance_urgent", urgent_alerts)
        return urgent_alerts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get urgent maintenance alerts: {str(e)}")
