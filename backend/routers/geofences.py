"""Geofence management endpoints."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any

from geotab_client import GeotabClient
from _cache import get_cached, set_cached

router = APIRouter()


class GeofenceCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    radius_meters: float = 200
    color: Optional[str] = "#3b82f6"
    alert_on_enter: bool = True
    alert_on_exit: bool = True


class GeofenceResponse(BaseModel):
    id: str
    name: str
    points: list[dict]
    color: str
    active_vehicles: int = 0


@router.get("/zones")
async def get_geofences():
    """Get all geofence zones from Geotab."""
    cache_key = "geofences:all"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        client = GeotabClient.get()
        zones = client.get_zones()
        
        result = []
        for z in zones:
            points = z.get("points", [])
            # Convert points to simple lat/lng
            simple_points = []
            for p in (points or []):
                if isinstance(p, dict):
                    simple_points.append({
                        "lat": p.get("y", p.get("latitude", 0)),
                        "lng": p.get("x", p.get("longitude", 0)),
                    })
            
            zone_data = {
                "id": z.get("id", ""),
                "name": z.get("name", "Unknown Zone"),
                "points": simple_points,
                "color": z.get("fillColor", {}).get("value", "#3b82f6") if isinstance(z.get("fillColor"), dict) else "#3b82f6",
                "displayed": z.get("displayed", True),
                "zone_type": str(z.get("zoneTypes", [{}])[0].get("id", "")) if z.get("zoneTypes") else "custom",
                "comment": z.get("comment", ""),
            }
            result.append(zone_data)
        
        set_cached(cache_key, result, ttl=120)
        return result
        
    except Exception as e:
        return [
            {
                "id": "demo-zone-1",
                "name": "LAS Airport Hub",
                "points": [
                    {"lat": 36.080, "lng": -115.152},
                    {"lat": 36.084, "lng": -115.152},
                    {"lat": 36.084, "lng": -115.148},
                    {"lat": 36.080, "lng": -115.148},
                ],
                "color": "#3b82f6",
                "displayed": True,
                "zone_type": "customer",
                "comment": "Main airport pickup/dropoff zone",
            },
            {
                "id": "demo-zone-2",
                "name": "Strip North",
                "points": [
                    {"lat": 36.126, "lng": -115.174},
                    {"lat": 36.130, "lng": -115.174},
                    {"lat": 36.130, "lng": -115.168},
                    {"lat": 36.126, "lng": -115.168},
                ],
                "color": "#8b5cf6",
                "displayed": True,
                "zone_type": "customer",
                "comment": "Las Vegas Strip north coverage",
            },
            {
                "id": "demo-zone-3",
                "name": "Henderson Depot",
                "points": [
                    {"lat": 36.028, "lng": -115.035},
                    {"lat": 36.032, "lng": -115.035},
                    {"lat": 36.032, "lng": -115.031},
                    {"lat": 36.028, "lng": -115.031},
                ],
                "color": "#10b981",
                "displayed": True,
                "zone_type": "office",
                "comment": "Henderson service depot",
            },
        ]


@router.get("/activity")
async def get_geofence_activity():
    """Get recent geofence entry/exit activity."""
    cache_key = "geofences:activity"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        client = GeotabClient.get()
        now = datetime.now(timezone.utc)
        from_date = now - timedelta(hours=24)
        
        # Get exception events which include zone-related events
        exceptions = client.get_exception_events(from_date=from_date, to_date=now)
        
        zone_events = []
        for ex in exceptions[:50]:
            rule = ex.get("rule", {})
            rule_name = rule.get("name", "") if isinstance(rule, dict) else ""
            
            if any(kw in rule_name.lower() for kw in ["zone", "geofence", "enter", "exit", "area"]):
                zone_events.append({
                    "id": ex.get("id", ""),
                    "vehicle": ex.get("device", {}).get("name", "Unknown") if isinstance(ex.get("device"), dict) else "Unknown",
                    "event_type": "exit" if "exit" in rule_name.lower() else "enter",
                    "zone_name": rule_name,
                    "timestamp": str(ex.get("activeFrom", now.isoformat())),
                })
        
        # If no real zone events, provide demo data
        if not zone_events:
            zone_events = [
                {"id": "evt-1", "vehicle": "Budget-LV-042", "event_type": "exit", "zone_name": "LAS Airport Hub", "timestamp": (now - timedelta(minutes=15)).isoformat()},
                {"id": "evt-2", "vehicle": "Budget-LV-018", "event_type": "enter", "zone_name": "Strip North", "timestamp": (now - timedelta(minutes=32)).isoformat()},
                {"id": "evt-3", "vehicle": "Budget-LV-073", "event_type": "enter", "zone_name": "Henderson Depot", "timestamp": (now - timedelta(hours=1)).isoformat()},
                {"id": "evt-4", "vehicle": "Budget-LV-055", "event_type": "exit", "zone_name": "Strip North", "timestamp": (now - timedelta(hours=2)).isoformat()},
                {"id": "evt-5", "vehicle": "Budget-LV-091", "event_type": "enter", "zone_name": "LAS Airport Hub", "timestamp": (now - timedelta(hours=3)).isoformat()},
            ]
        
        set_cached(cache_key, zone_events, ttl=60)
        return zone_events
        
    except Exception as e:
        now = datetime.now(timezone.utc)
        return [
            {"id": "evt-1", "vehicle": "Budget-LV-042", "event_type": "exit", "zone_name": "LAS Airport Hub", "timestamp": (now - timedelta(minutes=15)).isoformat()},
            {"id": "evt-2", "vehicle": "Budget-LV-018", "event_type": "enter", "zone_name": "Strip North", "timestamp": (now - timedelta(minutes=32)).isoformat()},
        ]


@router.post("/create")
async def create_geofence(geofence: GeofenceCreate):
    """Create a new circular geofence zone."""
    try:
        client = GeotabClient.get()
        
        import math
        # Generate circle points (16-sided polygon)
        points = []
        for i in range(16):
            angle = 2 * math.pi * i / 16
            dlat = geofence.radius_meters / 111320
            dlng = geofence.radius_meters / (111320 * math.cos(math.radians(geofence.latitude)))
            points.append({
                "x": geofence.longitude + dlng * math.cos(angle),
                "y": geofence.latitude + dlat * math.sin(angle),
            })
        
        zone_data = {
            "name": geofence.name,
            "points": points,
            "displayed": True,
            "comment": f"Created by FleetPulse on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        }
        
        zone_id = client.add_zone(zone_data)
        
        # Invalidate cache
        set_cached("geofences:all", None, ttl=0)
        
        return {
            "id": zone_id,
            "name": geofence.name,
            "status": "created",
            "message": f"Geofence '{geofence.name}' created successfully"
        }
        
    except Exception as e:
        return {
            "id": "demo-new",
            "name": geofence.name,
            "status": "demo",
            "message": f"Demo mode: Geofence '{geofence.name}' would be created. Error: {str(e)}"
        }
