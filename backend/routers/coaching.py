"""Driver coaching endpoints with automated recommendations."""

from fastapi import APIRouter, HTTPException

from models import (
    DriverCoachingDetail,
    DriverCoachingProfile,
    FleetCoachingSummary,
)
from services.coaching_service import (
    acknowledge_coaching,
    get_coaching_drivers,
    get_coaching_reports,
    get_driver_coaching_detail,
)

router = APIRouter()


@router.get("/drivers", response_model=list[DriverCoachingProfile])
async def coaching_drivers():
    """Get coaching profiles for all drivers with scores, trends, and recommendations."""
    try:
        return get_coaching_drivers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get coaching data: {str(e)}")


@router.get("/driver/{driver_id}", response_model=DriverCoachingDetail)
async def coaching_driver_detail(driver_id: str):
    """Get detailed coaching information for a specific driver."""
    try:
        return get_driver_coaching_detail(driver_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get driver coaching detail: {str(e)}")


@router.get("/reports", response_model=FleetCoachingSummary)
async def coaching_reports():
    """Get weekly coaching summary with fleet-wide metrics."""
    try:
        return get_coaching_reports()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get coaching reports: {str(e)}")


@router.post("/acknowledge/{driver_id}")
async def acknowledge_driver_coaching(driver_id: str):
    """Mark coaching recommendations as reviewed for a driver."""
    try:
        success = acknowledge_coaching(driver_id)
        if success:
            return {"status": "acknowledged", "driver_id": driver_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to acknowledge coaching")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge coaching: {str(e)}")