"""Data Connector endpoints – pre-aggregated fleet KPIs via Geotab OData."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from geotab_client import GeotabClient

router = APIRouter()

# OData base – we try servers 1-7, cache the working one
_ODATA_SERVER: str | None = None
_ODATA_SERVERS = [f"https://odata-connector-{i}.geotab.com/odata/v4/svc/" for i in range(1, 8)]


def _basic_auth() -> tuple[str, str]:
    gc = GeotabClient.get()
    username = f"{gc.database}/{gc.username}"
    password = gc.password
    return (username, password)


async def _find_server() -> str:
    global _ODATA_SERVER
    if _ODATA_SERVER:
        return _ODATA_SERVER
    auth = _basic_auth()
    async with httpx.AsyncClient(timeout=10) as client:
        for url in _ODATA_SERVERS:
            try:
                r = await client.get(url, auth=auth)
                if r.status_code == 200:
                    _ODATA_SERVER = url
                    return url
            except Exception:
                continue
    raise HTTPException(503, "Could not connect to any Data Connector server")


async def _odata_get(table: str, search: str = "last_14_day", select: str | None = None, top: int = 1000) -> list[dict]:
    base = await _find_server()
    auth = _basic_auth()
    params: dict[str, Any] = {"$search": search, "$top": str(top)}
    if select:
        params["$select"] = select
    url = f"{base}{table}"
    results: list[dict] = []
    async with httpx.AsyncClient(timeout=30) as client:
        while url:
            r = await client.get(url, auth=auth, params=params if url.startswith(base) else None)
            if r.status_code == 412:
                raise HTTPException(412, "Data Connector not activated. Install the add-in in MyGeotab Administration > System Settings > Add-Ins.")
            if r.status_code != 200:
                raise HTTPException(r.status_code, f"Data Connector error: {r.text[:500]}")
            data = r.json()
            results.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
            params = {}  # nextLink includes params
    return results


@router.get("/tables")
async def list_tables():
    """List available Data Connector tables."""
    base = await _find_server()
    auth = _basic_auth()
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(base, auth=auth)
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text[:500])
        return r.json()


@router.get("/vehicle-kpis")
async def vehicle_kpis(days: int = Query(14, ge=1, le=90)):
    """Fleet utilization KPIs per vehicle."""
    search = f"last_{days}_day" if days in (1, 7, 14, 30, 90) else "last_14_day"
    rows = await _odata_get("VehicleKpi_Daily", search=search)
    if not rows:
        return {"vehicles": [], "summary": {}}

    # Aggregate per vehicle
    from collections import defaultdict
    agg: dict[str, dict] = defaultdict(lambda: {
        "distance_km": 0, "drive_hours": 0, "idle_hours": 0, "trips": 0, "fuel_litres": 0
    })
    for r in rows:
        vid = r.get("DeviceSerialNumber") or r.get("VehicleName") or r.get("DeviceId", "unknown")
        a = agg[vid]
        a["vehicle_name"] = r.get("VehicleName", vid)
        a["distance_km"] += r.get("TotalDistance_Km", 0) or 0
        a["drive_hours"] += r.get("TotalDriveTime_Hours", 0) or 0
        a["idle_hours"] += r.get("TotalIdleTime_Hours", 0) or 0
        a["trips"] += r.get("TotalTrips", 0) or 0
        a["fuel_litres"] += r.get("TotalFuel_Litres", 0) or 0

    vehicles = sorted(agg.values(), key=lambda v: v["distance_km"], reverse=True)
    total_dist = sum(v["distance_km"] for v in vehicles)
    total_drive = sum(v["drive_hours"] for v in vehicles)
    total_idle = sum(v["idle_hours"] for v in vehicles)

    return {
        "vehicles": vehicles,
        "summary": {
            "total_vehicles": len(vehicles),
            "total_distance_km": round(total_dist, 1),
            "total_drive_hours": round(total_drive, 1),
            "total_idle_hours": round(total_idle, 1),
            "utilization_pct": round(total_drive / (total_drive + total_idle) * 100, 1) if (total_drive + total_idle) > 0 else 0,
        },
        "period_days": days,
    }


@router.get("/safety-scores")
async def safety_scores(days: int = Query(14, ge=1, le=90)):
    """Aggregated safety scores from Data Connector."""
    search = f"last_{days}_day" if days in (1, 7, 14, 30, 90) else "last_14_day"

    # Try fleet-level first, then vehicle-level
    fleet_rows = await _odata_get("FleetSafety_Daily", search=search)
    vehicle_rows = await _odata_get("VehicleSafety_Daily", search=search)

    return {
        "fleet_daily": fleet_rows[:30],
        "vehicle_scores": vehicle_rows[:100],
        "period_days": days,
    }


@router.get("/fault-trends")
async def fault_trends(days: int = Query(14, ge=1, le=90)):
    """Fault code trends from Data Connector."""
    search = f"last_{days}_day" if days in (1, 7, 14, 30, 90) else "last_14_day"
    rows = await _odata_get("FaultCode_Daily", search=search)
    return {"faults": rows[:200], "period_days": days}


@router.get("/trip-summary")
async def trip_summary(days: int = Query(14, ge=1, le=90)):
    """Trip summaries from Data Connector."""
    search = f"last_{days}_day" if days in (1, 7, 14, 30, 90) else "last_14_day"
    rows = await _odata_get("VehicleKpi_Daily", search=search,
                            select="VehicleName,TotalTrips,TotalDistance_Km,TotalDriveTime_Hours,TotalFuel_Litres")
    return {"trips": rows[:200], "period_days": days}
