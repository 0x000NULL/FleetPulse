"""Driver coaching service with automated recommendations and trends.

Optimized: fetches all exception events ONCE and filters locally,
with aggressive caching (5-min TTL) and timeout fallbacks.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from _cache import get_cached, set_cached
from geotab_client import GeotabClient
from models import (
    AlertSeverity,
    CoachingCategory,
    CoachingEventDetail,
    CoachingRecommendation,
    CoachingScores,
    CoachingStatus,
    CoachingTrend,
    DriverCoachingDetail,
    DriverCoachingProfile,
    FleetCoachingSummary,
    TrendDirection,
)

logger = logging.getLogger(__name__)

# Global memory for acknowledgments
_acknowledgments: dict[str, bool] = {}

# Event categorization mapping
_EVENT_CATEGORIES = {
    CoachingCategory.HARSH_BRAKING: ["hard brake", "harsh brake", "deceleration", "brake"],
    CoachingCategory.HARSH_ACCELERATION: ["harsh accel", "hard accel", "acceleration"],
    CoachingCategory.SPEEDING: ["speed", "posted", "speeding"],
    CoachingCategory.CORNERING: ["corner", "turning", "cornering"],
    CoachingCategory.SEATBELT: ["seat belt", "seatbelt", "belt"],
}

_RECOMMENDATIONS = {
    CoachingCategory.HARSH_BRAKING: [
        "Maintain 3-second following distance to avoid sudden braking",
        "Anticipate traffic patterns and brake gradually",
        "Use engine braking on downhill sections to reduce brake wear",
    ],
    CoachingCategory.HARSH_ACCELERATION: [
        "Accelerate smoothly and gradually from stops",
        "Use cruise control on highways to maintain consistent speed",
        "Plan ahead to avoid sudden speed changes",
    ],
    CoachingCategory.SPEEDING: [
        "Use GPS speed monitoring to stay aware of posted limits",
        "Set personal speed limits 5 mph below posted limits",
        "Plan extra time for trips to reduce speed pressure",
    ],
    CoachingCategory.CORNERING: [
        "Slow down before entering turns, not during",
        "Follow the racing line: outside-inside-outside",
        "Avoid hard steering inputs while braking or accelerating",
    ],
    CoachingCategory.SEATBELT: [
        "Always fasten seatbelt before starting engine",
        "Ensure proper seatbelt adjustment for safety and comfort",
        "Set a personal policy: no seatbelt, no driving",
    ],
}

_FUEL_IMPACT = {
    CoachingCategory.HARSH_BRAKING: 8.0,
    CoachingCategory.HARSH_ACCELERATION: 12.0,
    CoachingCategory.SPEEDING: 15.0,
    CoachingCategory.CORNERING: 5.0,
    CoachingCategory.SEATBELT: 0.0,
}


def _categorize_event(rule_name: str) -> CoachingCategory | None:
    lower = rule_name.lower()
    for category, keywords in _EVENT_CATEGORIES.items():
        if any(kw in lower for kw in keywords):
            return category
    return None


def _calculate_category_score(event_count: int) -> float:
    if event_count == 0:
        return 100.0
    penalty = min(event_count * 8 + (event_count ** 1.5), 100)
    return max(0.0, round(100 - penalty, 1))


def _calculate_coaching_scores(events: list[dict[str, Any]]) -> CoachingScores:
    event_counts: dict[CoachingCategory, int] = defaultdict(int)
    for event in events:
        rule_name = event.get("rule", {}).get("name", "")
        category = _categorize_event(rule_name)
        if category:
            event_counts[category] += 1
    return CoachingScores(
        harsh_braking=_calculate_category_score(event_counts[CoachingCategory.HARSH_BRAKING]),
        harsh_acceleration=_calculate_category_score(event_counts[CoachingCategory.HARSH_ACCELERATION]),
        speeding=_calculate_category_score(event_counts[CoachingCategory.SPEEDING]),
        cornering=_calculate_category_score(event_counts[CoachingCategory.CORNERING]),
        seatbelt=_calculate_category_score(event_counts[CoachingCategory.SEATBELT]),
    )


def _generate_recommendations(scores: CoachingScores) -> list[CoachingRecommendation]:
    recommendations = []
    categories = [
        (CoachingCategory.HARSH_BRAKING, scores.harsh_braking),
        (CoachingCategory.HARSH_ACCELERATION, scores.harsh_acceleration),
        (CoachingCategory.SPEEDING, scores.speeding),
        (CoachingCategory.CORNERING, scores.cornering),
        (CoachingCategory.SEATBELT, scores.seatbelt),
    ]
    categories.sort(key=lambda x: x[1])
    for i, (category, score) in enumerate(categories):
        if score < 85:
            messages = _RECOMMENDATIONS[category]
            if score < 50:
                message = messages[0]
            elif score < 70:
                message = messages[1] if len(messages) > 1 else messages[0]
            else:
                message = messages[-1]
            recommendations.append(
                CoachingRecommendation(
                    category=category,
                    priority=min(i + 1, 5),
                    message=message,
                    fuel_impact_pct=_FUEL_IMPACT[category],
                )
            )
    return recommendations[:3]


def _calculate_fuel_waste(scores: CoachingScores) -> float:
    total_waste = 0.0
    score_map = {
        CoachingCategory.HARSH_BRAKING: scores.harsh_braking,
        CoachingCategory.HARSH_ACCELERATION: scores.harsh_acceleration,
        CoachingCategory.SPEEDING: scores.speeding,
        CoachingCategory.CORNERING: scores.cornering,
    }
    for category, impact in _FUEL_IMPACT.items():
        if category in score_map:
            waste_multiplier = (100 - score_map[category]) / 100
            total_waste += impact * waste_multiplier
    return min(total_waste, 30.0)


def _avg_score(scores: CoachingScores) -> float:
    return (scores.harsh_braking + scores.harsh_acceleration +
            scores.speeding + scores.cornering + scores.seatbelt) / 5


def _fetch_all_events_cached(from_date: datetime, to_date: datetime, cache_key: str) -> list[dict]:
    """Fetch exception events with caching. Single API call for all devices."""
    cached = get_cached(cache_key, ttl=300)
    if cached is not None:
        return cached
    try:
        client = GeotabClient.get()
        events = client.get_exception_events(from_date, to_date)
        set_cached(cache_key, events)
        return events
    except (TimeoutError, Exception) as e:
        logger.warning(f"Failed to fetch events: {e}")
        return []


def _fetch_devices_cached() -> list[dict]:
    cached = get_cached("coaching:devices", ttl=300)
    if cached is not None:
        return cached
    try:
        client = GeotabClient.get()
        devices = client.get_devices()
        set_cached("coaching:devices", devices)
        return devices
    except (TimeoutError, Exception) as e:
        logger.warning(f"Failed to fetch devices: {e}")
        return []


def _filter_events_for_device(all_events: list[dict], device_id: str) -> list[dict]:
    return [e for e in all_events if e.get("device", {}).get("id") == device_id]


def get_coaching_drivers() -> list[DriverCoachingProfile]:
    """Get coaching profiles for all drivers. Optimized: 2 API calls total."""
    cached = get_cached("coaching:drivers", ttl=300)
    if cached is not None:
        return cached

    devices = _fetch_devices_cached()
    now = datetime.now(timezone.utc)

    # Fetch ALL events for the past 4 weeks in ONE call (covers trends too)
    four_weeks_ago = now - timedelta(days=28)
    all_events = _fetch_all_events_cached(four_weeks_ago, now, "coaching:events_4w")

    week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)

    profiles = []
    for device in devices:
        driver_id = device["id"]
        driver_name = device.get("name", "Unknown Driver")
        device_events = _filter_events_for_device(all_events, driver_id)

        # Current week events
        current_week_events = [
            e for e in device_events
            if _parse_event_date(e) >= week_start
        ]
        scores = _calculate_coaching_scores(current_week_events)
        overall_score = _avg_score(scores)

        # Trend: compare current week vs last week (no extra API calls!)
        last_week_events = [
            e for e in device_events
            if last_week_start <= _parse_event_date(e) < week_start
        ]
        last_scores = _calculate_coaching_scores(last_week_events)
        last_avg = _avg_score(last_scores)
        four_week_scores = _calculate_coaching_scores(device_events)
        four_week_avg = _avg_score(four_week_scores)

        if overall_score > last_avg + 5:
            direction = TrendDirection.IMPROVING
        elif overall_score < last_avg - 5:
            direction = TrendDirection.DECLINING
        else:
            direction = TrendDirection.STABLE

        trend = CoachingTrend(
            current_week=overall_score,
            last_week=last_avg,
            four_weeks_avg=four_week_avg,
            direction=direction,
        )

        if overall_score < 70:
            status = CoachingStatus.NEEDS_ATTENTION
        elif overall_score > 90 and direction == TrendDirection.IMPROVING:
            status = CoachingStatus.IMPROVED
        else:
            status = CoachingStatus.ON_TRACK

        recommendations = _generate_recommendations(scores)
        fuel_waste = _calculate_fuel_waste(scores)
        acknowledged = _acknowledgments.get(driver_id, False)

        profiles.append(
            DriverCoachingProfile(
                driver_id=driver_id,
                driver_name=driver_name,
                status=status,
                scores=scores,
                overall_score=overall_score,
                recommendations=recommendations,
                trend=trend,
                events_this_week=len(current_week_events),
                fuel_waste_pct=fuel_waste,
                acknowledged=acknowledged,
            )
        )

    profiles.sort(key=lambda x: x.overall_score)
    set_cached("coaching:drivers", profiles)
    return profiles


def get_driver_coaching_detail(driver_id: str) -> DriverCoachingDetail:
    """Get detailed coaching for a specific driver. Uses cached data."""
    cached = get_cached(f"coaching:detail:{driver_id}", ttl=300)
    if cached is not None:
        return cached

    devices = _fetch_devices_cached()
    now = datetime.now(timezone.utc)
    month_start = now - timedelta(days=30)

    all_events = _fetch_all_events_cached(month_start, now, "coaching:events_30d")
    device_events = _filter_events_for_device(all_events, driver_id)

    scores = _calculate_coaching_scores(device_events)
    recommendations = _generate_recommendations(scores)

    # Trend from cached 4-week data
    four_weeks_ago = now - timedelta(days=28)
    all_4w = _fetch_all_events_cached(four_weeks_ago, now, "coaching:events_4w")
    dev_4w = _filter_events_for_device(all_4w, driver_id)

    week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)
    current_avg = _avg_score(_calculate_coaching_scores([e for e in dev_4w if _parse_event_date(e) >= week_start]))
    last_avg = _avg_score(_calculate_coaching_scores([e for e in dev_4w if last_week_start <= _parse_event_date(e) < week_start]))
    four_week_avg = _avg_score(_calculate_coaching_scores(dev_4w))

    if current_avg > last_avg + 5:
        direction = TrendDirection.IMPROVING
    elif current_avg < last_avg - 5:
        direction = TrendDirection.DECLINING
    else:
        direction = TrendDirection.STABLE

    trend = CoachingTrend(current_week=current_avg, last_week=last_avg,
                          four_weeks_avg=four_week_avg, direction=direction)

    # Event details
    event_details = []
    for event in device_events[-20:]:
        rule_name = event.get("rule", {}).get("name", "")
        category = _categorize_event(rule_name)
        if category:
            location = "Unknown Location"
            if "latitude" in event and "longitude" in event:
                location = f"Lat: {event['latitude']:.3f}, Lon: {event['longitude']:.3f}"
            severity = AlertSeverity.MEDIUM
            if "harsh" in rule_name.lower() or "hard" in rule_name.lower():
                severity = AlertSeverity.HIGH
            elif "speed" in rule_name.lower():
                severity = AlertSeverity.CRITICAL
            event_details.append(
                CoachingEventDetail(
                    timestamp=datetime.fromisoformat(event.get("activeFrom", now.isoformat())),
                    category=category, location=location,
                    severity=severity, description=rule_name,
                )
            )

    # Weekly stats from local filtering
    weekly_stats = {}
    for i in range(4):
        ws = now - timedelta(days=(i + 1) * 7)
        we = now - timedelta(days=i * 7)
        week_evts = [e for e in dev_4w if ws <= _parse_event_date(e) < we]
        weekly_stats[f"Week {4 - i}"] = len(week_evts)

    driver_name = next((d.get("name", "Unknown") for d in devices if d["id"] == driver_id), "Unknown")

    result = DriverCoachingDetail(
        driver_id=driver_id, driver_name=driver_name,
        scores=scores, trend=trend, recommendations=recommendations,
        recent_events=event_details, weekly_stats=weekly_stats,
    )
    set_cached(f"coaching:detail:{driver_id}", result)
    return result


def get_coaching_reports() -> FleetCoachingSummary:
    """Get weekly coaching summary. Uses cached driver profiles."""
    cached = get_cached("coaching:reports", ttl=300)
    if cached is not None:
        return cached

    profiles = get_coaching_drivers()
    total_drivers = len(profiles)
    if not profiles:
        return FleetCoachingSummary(
            total_drivers=0, needs_attention=0, on_track=0, improved=0,
            average_score=0, best_improved=[], worst_performers=[],
            fleet_fuel_savings_potential=0,
        )

    needs_attention = sum(1 for p in profiles if p.status == CoachingStatus.NEEDS_ATTENTION)
    on_track = sum(1 for p in profiles if p.status == CoachingStatus.ON_TRACK)
    improved = sum(1 for p in profiles if p.status == CoachingStatus.IMPROVED)
    average_score = sum(p.overall_score for p in profiles) / total_drivers

    improving = [p for p in profiles if p.trend.direction == TrendDirection.IMPROVING]
    improving.sort(key=lambda x: x.trend.current_week - x.trend.last_week, reverse=True)
    best_improved = [p.driver_name for p in improving[:3]]
    worst_performers = [p.driver_name for p in profiles[-3:] if p.overall_score < 60]

    avg_fuel_waste = sum(p.fuel_waste_pct for p in profiles) / total_drivers
    fleet_fuel_savings = min(avg_fuel_waste * 0.8, 25.0)

    result = FleetCoachingSummary(
        total_drivers=total_drivers, needs_attention=needs_attention,
        on_track=on_track, improved=improved, average_score=average_score,
        best_improved=best_improved, worst_performers=worst_performers,
        fleet_fuel_savings_potential=fleet_fuel_savings,
    )
    set_cached("coaching:reports", result)
    return result


def acknowledge_coaching(driver_id: str) -> bool:
    _acknowledgments[driver_id] = True
    return True


def _parse_event_date(event: dict) -> datetime:
    try:
        val = event.get("activeFrom", "")
        if isinstance(val, datetime):
            return val
        return datetime.fromisoformat(str(val).replace("Z", "+00:00"))
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)
