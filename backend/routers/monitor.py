"""Agentic Monitor endpoints — intelligent anomaly detection."""

from fastapi import APIRouter, Query

from models import Alert
from services.monitor_service import get_monitor_alerts, get_monitor_status, run_check_now

router = APIRouter()


@router.get("/alerts", response_model=list[Alert])
async def monitor_alerts(limit: int = Query(50, ge=1, le=200)):
    return get_monitor_alerts(limit=limit)


@router.get("/status")
async def monitor_status():
    return get_monitor_status()


@router.post("/check")
async def trigger_check():
    """Manually trigger a monitor check cycle."""
    alerts = run_check_now()
    return {"alerts_generated": len(alerts), "alerts": [a.model_dump() for a in alerts]}
