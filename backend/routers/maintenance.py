"""Predictive maintenance endpoints."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from geotab_client import GeotabClient
from models import (
    MaintenancePrediction, 
    VehicleMaintenanceDetail, 
    MaintenanceCost, 
    UrgentMaintenanceAlert,
    MaintenanceType,
    UrgencyLevel
)

router = APIRouter()

# Standard maintenance intervals
MAINTENANCE_INTERVALS = {
    "oil_change": {"miles": 5000, "months": 6},
    "brake_service": {"miles": 30000, "months": 24},
    "tire_rotation": {"miles": 7500, "months": 12},
    "transmission_service": {"miles": 60000, "months": 48}
}

# Industry average costs
MAINTENANCE_COSTS = {
    "oil_change": 75,
    "brake_service": 600,  # $300 per axle * 2 axles
    "tire_rotation": 25,
    "transmission_service": 300,
    "tires_replacement": 600
}


def calculate_maintenance_due_date(last_service: datetime, odometer_at_service: float, 
                                 current_odometer: float, service_type: str) -> tuple[datetime, bool]:
    """Calculate when maintenance is due based on mileage and time."""
    intervals = MAINTENANCE_INTERVALS[service_type]
    
    # Calculate due date by mileage
    miles_since_service = current_odometer - odometer_at_service
    miles_remaining = intervals["miles"] - miles_since_service
    
    # Estimate miles per day (assume 50 miles/day average)
    avg_miles_per_day = 50
    days_until_due = max(0, miles_remaining / avg_miles_per_day)
    due_date_by_miles = datetime.now(timezone.utc) + timedelta(days=days_until_due)
    
    # Calculate due date by time
    due_date_by_time = last_service + timedelta(days=intervals["months"] * 30)
    
    # Use the earlier of the two dates
    due_date = min(due_date_by_miles, due_date_by_time)
    is_overdue = due_date < datetime.now(timezone.utc)
    
    return due_date, is_overdue


def get_urgency_level(due_date: datetime, has_fault_codes: bool = False) -> UrgencyLevel:
    """Determine urgency level based on due date and fault codes."""
    if has_fault_codes:
        return UrgencyLevel.CRITICAL
    
    days_until_due = (due_date - datetime.now(timezone.utc)).days
    
    if days_until_due < 0:  # Overdue
        return UrgencyLevel.CRITICAL
    elif days_until_due <= 7:
        return UrgencyLevel.HIGH
    elif days_until_due <= 30:
        return UrgencyLevel.MEDIUM
    else:
        return UrgencyLevel.LOW


@router.get("/predictions", response_model=List[MaintenancePrediction])
async def get_maintenance_predictions():
    """Get maintenance predictions for all vehicles."""
    try:
        client = GeotabClient.get()
        devices = client.get_devices()
        predictions = []
        
        for device in devices:
            device_id = device.get("id", "")
            device_name = device.get("name", "Unknown Vehicle")
            
            # Get current odometer reading
            try:
                odometer_data = client.get_status_data(
                    diagnostic_id="DiagnosticOdometerId",
                    from_date=datetime.now(timezone.utc) - timedelta(days=1)
                )
                current_odometer = 0
                if odometer_data:
                    # Convert from km to miles
                    current_odometer = float(odometer_data[-1].get("data", 0)) * 0.621371
            except:
                current_odometer = 0
            
            # Get engine hours
            try:
                engine_hours_data = client.get_status_data(
                    diagnostic_id="DiagnosticEngineHoursId",
                    from_date=datetime.now(timezone.utc) - timedelta(days=1)
                )
                engine_hours = 0
                if engine_hours_data:
                    engine_hours = float(engine_hours_data[-1].get("data", 0))
            except:
                engine_hours = 0
            
            # Get active fault codes
            try:
                fault_data = client.api.get('FaultData', search={
                    'deviceSearch': {'id': device_id},
                    'fromDate': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
                })
                has_fault_codes = len(fault_data) > 0
                active_fault_count = len([f for f in fault_data if not f.get('dismissDateTime')])
            except:
                has_fault_codes = False
                active_fault_count = 0
            
            # Calculate maintenance predictions
            # Simulate last service dates (in real app, this would come from maintenance records)
            now = datetime.now(timezone.utc)
            base_date = now - timedelta(days=90)  # Assume last service 3 months ago
            base_odometer = max(0, current_odometer - 3000)  # 3000 miles ago
            
            upcoming_services = []
            
            for service_type in MAINTENANCE_INTERVALS.keys():
                due_date, is_overdue = calculate_maintenance_due_date(
                    base_date, base_odometer, current_odometer, service_type
                )
                urgency = get_urgency_level(due_date, has_fault_codes)
                
                upcoming_services.append({
                    "service_type": service_type,
                    "due_date": due_date,
                    "is_overdue": is_overdue,
                    "urgency": urgency,
                    "estimated_cost": MAINTENANCE_COSTS[service_type]
                })
            
            prediction = MaintenancePrediction(
                vehicle_id=device_id,
                vehicle_name=device_name,
                current_odometer=current_odometer,
                engine_hours=engine_hours,
                upcoming_services=upcoming_services,
                has_active_fault_codes=has_fault_codes,
                active_fault_count=active_fault_count
            )
            predictions.append(prediction)
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get maintenance predictions: {str(e)}")


@router.get("/vehicle/{vehicle_id}", response_model=VehicleMaintenanceDetail)
async def get_vehicle_maintenance_detail(vehicle_id: str):
    """Get detailed maintenance timeline for a specific vehicle."""
    try:
        client = GeotabClient.get()
        
        # Get device details
        devices = client.get_devices()
        device = next((d for d in devices if d.get("id") == vehicle_id), None)
        if not device:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        device_name = device.get("name", "Unknown Vehicle")
        
        # Get current odometer and engine hours (same as predictions endpoint)
        try:
            odometer_data = client.get_status_data(
                diagnostic_id="DiagnosticOdometerId",
                from_date=datetime.now(timezone.utc) - timedelta(days=1)
            )
            current_odometer = 0
            if odometer_data:
                current_odometer = float(odometer_data[-1].get("data", 0)) * 0.621371
        except:
            current_odometer = 0
        
        try:
            engine_hours_data = client.get_status_data(
                diagnostic_id="DiagnosticEngineHoursId",
                from_date=datetime.now(timezone.utc) - timedelta(days=1)
            )
            engine_hours = 0
            if engine_hours_data:
                engine_hours = float(engine_hours_data[-1].get("data", 0))
        except:
            engine_hours = 0
        
        # Get fault codes with details
        try:
            fault_data = client.api.get('FaultData', search={
                'deviceSearch': {'id': vehicle_id},
                'fromDate': (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            })
            
            active_faults = []
            for fault in fault_data:
                if not fault.get('dismissDateTime'):  # Active fault
                    active_faults.append({
                        "code": fault.get("diagnostic", {}).get("code", "Unknown"),
                        "description": fault.get("diagnostic", {}).get("name", "Unknown Fault"),
                        "timestamp": fault.get("dateTime", datetime.now(timezone.utc)),
                        "severity": "high"  # Default severity
                    })
        except:
            active_faults = []
        
        # Generate maintenance history (simulated for demo)
        now = datetime.now(timezone.utc)
        maintenance_history = []
        
        for i, service_type in enumerate(MAINTENANCE_INTERVALS.keys()):
            # Simulate past maintenance
            past_date = now - timedelta(days=90 + i * 30)
            maintenance_history.append({
                "service_type": service_type,
                "date": past_date,
                "odometer_at_service": max(0, current_odometer - (3000 - i * 500)),
                "cost": MAINTENANCE_COSTS[service_type],
                "notes": f"Completed {service_type.replace('_', ' ')} service"
            })
        
        # Calculate upcoming maintenance (same logic as predictions)
        base_date = now - timedelta(days=90)
        base_odometer = max(0, current_odometer - 3000)
        
        upcoming_services = []
        for service_type in MAINTENANCE_INTERVALS.keys():
            due_date, is_overdue = calculate_maintenance_due_date(
                base_date, base_odometer, current_odometer, service_type
            )
            urgency = get_urgency_level(due_date, len(active_faults) > 0)
            
            upcoming_services.append({
                "service_type": service_type,
                "due_date": due_date,
                "is_overdue": is_overdue,
                "urgency": urgency,
                "estimated_cost": MAINTENANCE_COSTS[service_type]
            })
        
        return VehicleMaintenanceDetail(
            vehicle_id=vehicle_id,
            vehicle_name=device_name,
            current_odometer=current_odometer,
            engine_hours=engine_hours,
            upcoming_services=upcoming_services,
            maintenance_history=maintenance_history,
            active_fault_codes=active_faults,
            last_service_date=base_date
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vehicle maintenance detail: {str(e)}")


@router.get("/costs", response_model=MaintenanceCost)
async def get_maintenance_costs():
    """Get estimated maintenance costs for the next 3 months."""
    try:
        client = GeotabClient.get()
        devices = client.get_devices()
        
        total_cost_next_month = 0
        total_cost_next_3_months = 0
        cost_breakdown = {}
        
        now = datetime.now(timezone.utc)
        next_month = now + timedelta(days=30)
        next_3_months = now + timedelta(days=90)
        
        for device in devices:
            device_id = device.get("id", "")
            
            # Get current odometer (simplified for cost calculation)
            current_odometer = 15000  # Simulate average mileage
            base_date = now - timedelta(days=90)
            base_odometer = current_odometer - 3000
            
            for service_type in MAINTENANCE_INTERVALS.keys():
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
        
        return MaintenanceCost(
            total_cost_next_month=total_cost_next_month,
            total_cost_next_3_months=total_cost_next_3_months,
            cost_breakdown=cost_breakdown,
            average_monthly_cost=total_cost_next_3_months / 3
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get maintenance costs: {str(e)}")


@router.get("/urgent", response_model=List[UrgentMaintenanceAlert])
async def get_urgent_maintenance():
    """Get vehicles with overdue maintenance or active fault codes."""
    try:
        client = GeotabClient.get()
        devices = client.get_devices()
        urgent_alerts = []
        
        for device in devices:
            device_id = device.get("id", "")
            device_name = device.get("name", "Unknown Vehicle")
            
            # Check for active fault codes
            try:
                fault_data = client.api.get('FaultData', search={
                    'deviceSearch': {'id': device_id},
                    'fromDate': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
                })
                active_faults = [f for f in fault_data if not f.get('dismissDateTime')]
            except:
                active_faults = []
            
            # Check for overdue maintenance
            current_odometer = 15000  # Simulate
            base_date = datetime.now(timezone.utc) - timedelta(days=90)
            base_odometer = current_odometer - 3000
            
            overdue_services = []
            urgent_services = []
            
            for service_type in MAINTENANCE_INTERVALS.keys():
                due_date, is_overdue = calculate_maintenance_due_date(
                    base_date, base_odometer, current_odometer, service_type
                )
                
                if is_overdue:
                    overdue_services.append({
                        "service_type": service_type,
                        "due_date": due_date,
                        "days_overdue": (datetime.now(timezone.utc) - due_date).days
                    })
                elif (due_date - datetime.now(timezone.utc)).days <= 7:  # Due within a week
                    urgent_services.append({
                        "service_type": service_type,
                        "due_date": due_date,
                        "days_until_due": (due_date - datetime.now(timezone.utc)).days
                    })
            
            # Create alert if there are urgent issues
            if active_faults or overdue_services or urgent_services:
                urgency = UrgencyLevel.CRITICAL if (active_faults or overdue_services) else UrgencyLevel.HIGH
                
                alert = UrgentMaintenanceAlert(
                    vehicle_id=device_id,
                    vehicle_name=device_name,
                    urgency=urgency,
                    active_fault_codes=[{
                        "code": f.get("diagnostic", {}).get("code", "Unknown"),
                        "description": f.get("diagnostic", {}).get("name", "Unknown Fault")
                    } for f in active_faults],
                    overdue_services=overdue_services,
                    urgent_services=urgent_services,
                    estimated_repair_cost=sum(MAINTENANCE_COSTS.get(s["service_type"], 0) for s in overdue_services + urgent_services)
                )
                urgent_alerts.append(alert)
        
        # Sort by urgency (critical first)
        urgent_alerts.sort(key=lambda x: (x.urgency.value, x.vehicle_name))
        
        return urgent_alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get urgent maintenance alerts: {str(e)}")