"""Gamification service — points, badges, leaderboards, challenges."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from models import Badge, Challenge, DriverScore, LocationRanking
from services.safety_service import get_safety_scores
from services.fleet_service import LOCATIONS, get_vehicles

# ── Badge definitions ──────────────────────────────────────────
BADGE_DEFS = [
    Badge(id="speed_free", name="Speed Demon Free", description="No speeding events for 7 days", icon="🏅"),
    Badge(id="smooth_op", name="Smooth Operator", description="No harsh braking for 7 days", icon="🎯"),
    Badge(id="eco_champ", name="Eco Champion", description="Best fuel efficiency in fleet", icon="🌿"),
    Badge(id="perfect_week", name="Perfect Week", description="100 safety score for a full week", icon="⭐"),
    Badge(id="road_warrior", name="Road Warrior", description="Most miles driven safely", icon="🛣️"),
]


def _compute_points(score: float, event_count: int) -> int:
    """Base 1000 pts * safety_score%, minus 50 per event."""
    return max(0, int(score * 10) - event_count * 50)


def get_leaderboard() -> list[DriverScore]:
    """Build driver leaderboard from safety scores. Uses vehicle as proxy for driver."""
    scores = get_safety_scores(days=7)
    leaderboard: list[DriverScore] = []

    # Find best score for eco badge
    best_score = max((s.score for s in scores), default=100)

    for s in scores:
        badges: list[Badge] = []
        now = datetime.now(timezone.utc)

        if s.breakdown.speeding == 0:
            b = BADGE_DEFS[0].model_copy()
            b.earned = True
            b.earned_at = now
            badges.append(b)

        if s.breakdown.harsh_braking == 0:
            b = BADGE_DEFS[1].model_copy()
            b.earned = True
            b.earned_at = now
            badges.append(b)

        if s.score == best_score:
            b = BADGE_DEFS[2].model_copy()
            b.earned = True
            b.earned_at = now
            badges.append(b)

        if s.score == 100:
            b = BADGE_DEFS[3].model_copy()
            b.earned = True
            b.earned_at = now
            badges.append(b)

        leaderboard.append(
            DriverScore(
                driver_id=s.vehicle_id,
                driver_name=s.vehicle_name,
                points=_compute_points(s.score, s.event_count),
                safety_score=s.score,
                badges=badges,
                rank=0,
            )
        )

    leaderboard.sort(key=lambda d: d.points, reverse=True)
    for i, d in enumerate(leaderboard, 1):
        d.rank = i

    return leaderboard


def get_active_challenges() -> list[Challenge]:
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=7)
    return [
        Challenge(
            id="weekly_safe",
            title="Safe Week Challenge",
            description="Maintain a 90+ safety score all week",
            start_date=week_start,
            end_date=week_end,
            target_metric="safety_score",
            current_value=0,
            target_value=90,
        ),
        Challenge(
            id="zero_speeding",
            title="Zero Speeding",
            description="Complete the week with zero speeding events",
            start_date=week_start,
            end_date=week_end,
            target_metric="speeding_events",
            current_value=0,
            target_value=0,
        ),
    ]


def get_location_rankings() -> list[LocationRanking]:
    scores = get_safety_scores(days=7)
    vehicles = get_vehicles()
    veh_location = {v.id: v.location_name for v in vehicles}

    loc_scores: dict[str, list[float]] = {loc["name"]: [] for loc in LOCATIONS}
    loc_points: dict[str, int] = {loc["name"]: 0 for loc in LOCATIONS}

    for s in scores:
        loc = veh_location.get(s.vehicle_id)
        if loc and loc in loc_scores:
            loc_scores[loc].append(s.score)
            loc_points[loc] += _compute_points(s.score, s.event_count)

    rankings: list[LocationRanking] = []
    for name in loc_scores:
        vals = loc_scores[name]
        rankings.append(
            LocationRanking(
                location_name=name,
                avg_safety_score=round(sum(vals) / max(len(vals), 1), 1),
                total_points=loc_points[name],
                rank=0,
            )
        )

    rankings.sort(key=lambda r: r.avg_safety_score, reverse=True)
    for i, r in enumerate(rankings, 1):
        r.rank = i

    return rankings
