"""Gamification endpoints — leaderboards, badges, challenges."""

from fastapi import APIRouter

from models import Challenge, DriverScore, LocationRanking
from services.gamification_service import get_active_challenges, get_leaderboard, get_location_rankings

router = APIRouter()


@router.get("/leaderboard", response_model=list[DriverScore])
async def leaderboard():
    return get_leaderboard()


@router.get("/challenges", response_model=list[Challenge])
async def challenges():
    return get_active_challenges()


@router.get("/location-rankings", response_model=list[LocationRanking])
async def location_rankings():
    return get_location_rankings()
