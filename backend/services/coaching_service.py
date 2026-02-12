"""Driver coaching service with automated recommendations and trends."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

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

# Global memory for acknowledgments (in a real app, use Redis/database)
_acknowledgments: dict[str, bool] = {}

# Event categorization mapping
_EVENT_CATEGORIES = {
    CoachingCategory.HARSH_BRAKING: ["hard brake", "harsh brake", "deceleration", "brake"],
    CoachingCategory.HARSH_ACCELERATION: ["harsh accel", "hard accel", "acceleration"],
    CoachingCategory.SPEEDING: ["speed", "posted", "speeding"],
    CoachingCategory.CORNERING: ["corner", "turning", "cornering"],
    CoachingCategory.SEATBELT: ["seat belt", "seatbelt", "belt"],
}

# Coaching recommendations by category
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

# Fuel impact estimates for different driving behaviors (percentage increase)
_FUEL_IMPACT = {
    CoachingCategory.HARSH_BRAKING: 8.0,
    CoachingCategory.HARSH_ACCELERATION: 12.0,
    CoachingCategory.SPEEDING: 15.0,
    CoachingCategory.CORNERING: 5.0,
    CoachingCategory.SEATBELT: 0.0,  # No direct fuel impact
}


def _categorize_event(rule_name: str) -> CoachingCategory | None:
    """Categorize a safety event by rule name."""
    lower = rule_name.lower()
    for category, keywords in _EVENT_CATEGORIES.items():
        if any(kw in lower for kw in keywords):
            return category
    return None


def _calculate_category_score(event_count: int, max_events: int = 10) -> float:
    """Calculate 0-100 score for a category based on event count."""
    if event_count == 0:
        return 100.0
    # Exponential decay: each event has diminishing impact
    penalty = min(event_count * 8 + (event_count ** 1.5), 100)
    return max(0.0, round(100 - penalty, 1))


def _get_driver_events(
    driver_id: str, from_date: datetime, to_date: datetime
) -> list[dict[str, Any]]:
    """Get safety events for a specific driver in date range."""
    client = GeotabClient.get()
    all_events = client.get_exception_events(from_date, to_date)
    
    # Filter events for this driver (assuming device.id maps to driver)
    # In real implementation, you'd need proper driver-to-device mapping
    driver_events = [
        e for e in all_events 
        if e.get("device", {}).get("id") == driver_id
    ]
    return driver_events


def _calculate_coaching_scores(events: list[dict[str, Any]]) -> CoachingScores:
    """Calculate coaching scores from safety events."""
    event_counts = defaultdict(int)
    
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
    """Generate coaching recommendations based on scores."""
    recommendations = []
    
    # Check each category and generate recommendations for poor scores
    categories = [
        (CoachingCategory.HARSH_BRAKING, scores.harsh_braking),
        (CoachingCategory.HARSH_ACCELERATION, scores.harsh_acceleration),
        (CoachingCategory.SPEEDING, scores.speeding),
        (CoachingCategory.CORNERING, scores.cornering),
        (CoachingCategory.SEATBELT, scores.seatbelt),
    ]
    
    # Sort by score (worst first) to prioritize recommendations
    categories.sort(key=lambda x: x[1])
    
    for i, (category, score) in enumerate(categories):
        if score < 85:  # Only recommend if score is below 85
            priority = min(i + 1, 5)  # 1=highest priority
            messages = _RECOMMENDATIONS[category]
            # Pick recommendation based on score level
            if score < 50:
                message = messages[0]  # Most critical advice
            elif score < 70:
                message = messages[1] if len(messages) > 1 else messages[0]
            else:
                message = messages[-1]  # Least critical advice
                
            recommendations.append(
                CoachingRecommendation(
                    category=category,
                    priority=priority,
                    message=message,
                    fuel_impact_pct=_FUEL_IMPACT[category],
                )
            )
    
    return recommendations[:3]  # Limit to top 3 recommendations


def _calculate_fuel_waste(scores: CoachingScores) -> float:
    """Calculate estimated fuel waste percentage based on scores."""
    total_waste = 0.0
    
    # Calculate weighted fuel impact based on how bad each score is
    for category, impact in _FUEL_IMPACT.items():
        if category == CoachingCategory.HARSH_BRAKING:
            score = scores.harsh_braking
        elif category == CoachingCategory.HARSH_ACCELERATION:
            score = scores.harsh_acceleration
        elif category == CoachingCategory.SPEEDING:
            score = scores.speeding
        elif category == CoachingCategory.CORNERING:
            score = scores.cornering
        else:
            continue
            
        # Convert score to waste multiplier (100 = 0%, 0 = 100% of impact)
        waste_multiplier = (100 - score) / 100
        total_waste += impact * waste_multiplier
    
    return min(total_waste, 30.0)  # Cap at 30%


def _get_trend_data(driver_id: str) -> CoachingTrend:
    """Calculate trend data for a driver."""
    now = datetime.now(timezone.utc)
    
    # Current week
    current_week_start = now - timedelta(days=7)
    current_events = _get_driver_events(driver_id, current_week_start, now)
    current_scores = _calculate_coaching_scores(current_events)
    current_avg = (
        current_scores.harsh_braking + current_scores.harsh_acceleration + 
        current_scores.speeding + current_scores.cornering + current_scores.seatbelt
    ) / 5
    
    # Last week
    last_week_start = now - timedelta(days=14)
    last_week_end = now - timedelta(days=7)
    last_events = _get_driver_events(driver_id, last_week_start, last_week_end)
    last_scores = _calculate_coaching_scores(last_events)
    last_avg = (
        last_scores.harsh_braking + last_scores.harsh_acceleration + 
        last_scores.speeding + last_scores.cornering + last_scores.seatbelt
    ) / 5
    
    # 4-week average
    four_weeks_start = now - timedelta(days=28)
    four_week_events = _get_driver_events(driver_id, four_weeks_start, now)
    four_week_scores = _calculate_coaching_scores(four_week_events)
    four_week_avg = (
        four_week_scores.harsh_braking + four_week_scores.harsh_acceleration + 
        four_week_scores.speeding + four_week_scores.cornering + four_week_scores.seatbelt
    ) / 5
    
    # Determine trend direction
    if current_avg > last_avg + 5:
        direction = TrendDirection.IMPROVING
    elif current_avg < last_avg - 5:
        direction = TrendDirection.DECLINING
    else:
        direction = TrendDirection.STABLE
    
    return CoachingTrend(
        current_week=current_avg,
        last_week=last_avg,
        four_weeks_avg=four_week_avg,
        direction=direction,
    )


def get_coaching_drivers() -> list[DriverCoachingProfile]:
    """Get coaching profiles for all drivers."""
    client = GeotabClient.get()
    devices = client.get_devices()
    
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=7)
    
    profiles = []
    
    for device in devices:
        driver_id = device["id"]
        driver_name = device.get("name", "Unknown Driver")
        
        # Get events for this week
        events = _get_driver_events(driver_id, week_start, now)
        scores = _calculate_coaching_scores(events)
        
        # Calculate overall score
        overall_score = (
            scores.harsh_braking + scores.harsh_acceleration + 
            scores.speeding + scores.cornering + scores.seatbelt
        ) / 5
        
        # Determine status
        if overall_score < 70:
            status = CoachingStatus.NEEDS_ATTENTION
        elif overall_score > 90:
            # Check if improving from last week
            trend = _get_trend_data(driver_id)
            if trend.direction == TrendDirection.IMPROVING:
                status = CoachingStatus.IMPROVED
            else:
                status = CoachingStatus.ON_TRACK
        else:
            status = CoachingStatus.ON_TRACK
        
        recommendations = _generate_recommendations(scores)
        trend = _get_trend_data(driver_id)
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
                events_this_week=len(events),
                fuel_waste_pct=fuel_waste,
                acknowledged=acknowledged,
            )
        )
    
    # Sort by score (worst first for attention)
    profiles.sort(key=lambda x: x.overall_score)
    return profiles


def get_driver_coaching_detail(driver_id: str) -> DriverCoachingDetail:
    """Get detailed coaching information for a specific driver."""
    client = GeotabClient.get()
    
    now = datetime.now(timezone.utc)
    month_start = now - timedelta(days=30)
    
    # Get recent events
    events = _get_driver_events(driver_id, month_start, now)
    scores = _calculate_coaching_scores(events)
    recommendations = _generate_recommendations(scores)
    trend = _get_trend_data(driver_id)
    
    # Convert events to details
    event_details = []
    for event in events[-20:]:  # Last 20 events
        rule_name = event.get("rule", {}).get("name", "")
        category = _categorize_event(rule_name)
        if category:
            # Try to extract location info (simplified)
            location = "Unknown Location"
            if "latitude" in event and "longitude" in event:
                lat = event["latitude"]
                lon = event["longitude"]
                location = f"Lat: {lat:.3f}, Lon: {lon:.3f}"
            
            # Determine severity based on rule
            severity = AlertSeverity.MEDIUM
            if "harsh" in rule_name.lower() or "hard" in rule_name.lower():
                severity = AlertSeverity.HIGH
            elif "speed" in rule_name.lower():
                severity = AlertSeverity.CRITICAL
            
            event_details.append(
                CoachingEventDetail(
                    timestamp=datetime.fromisoformat(event.get("activeFrom", now.isoformat())),
                    category=category,
                    location=location,
                    severity=severity,
                    description=rule_name,
                )
            )
    
    # Calculate weekly stats
    weekly_stats = {}
    for i in range(4):
        week_start = now - timedelta(days=(i + 1) * 7)
        week_end = now - timedelta(days=i * 7)
        week_events = _get_driver_events(driver_id, week_start, week_end)
        week_name = f"Week {4-i}"
        weekly_stats[week_name] = len(week_events)
    
    # Get driver name
    devices = client.get_devices()
    driver_name = next((d.get("name", "Unknown") for d in devices if d["id"] == driver_id), "Unknown")
    
    return DriverCoachingDetail(
        driver_id=driver_id,
        driver_name=driver_name,
        scores=scores,
        trend=trend,
        recommendations=recommendations,
        recent_events=event_details,
        weekly_stats=weekly_stats,
    )


def get_coaching_reports() -> FleetCoachingSummary:
    """Get weekly coaching summary for the fleet."""
    profiles = get_coaching_drivers()
    
    total_drivers = len(profiles)
    needs_attention = sum(1 for p in profiles if p.status == CoachingStatus.NEEDS_ATTENTION)
    on_track = sum(1 for p in profiles if p.status == CoachingStatus.ON_TRACK)
    improved = sum(1 for p in profiles if p.status == CoachingStatus.IMPROVED)
    
    average_score = sum(p.overall_score for p in profiles) / total_drivers if profiles else 0.0
    
    # Best improved (top 3 improving drivers)
    improving_drivers = [p for p in profiles if p.trend.direction == TrendDirection.IMPROVING]
    improving_drivers.sort(key=lambda x: x.trend.current_week - x.trend.last_week, reverse=True)
    best_improved = [p.driver_name for p in improving_drivers[:3]]
    
    # Worst performers (bottom 3 by score)
    worst_performers = [p.driver_name for p in profiles[-3:] if p.overall_score < 60]
    
    # Fleet fuel savings potential
    avg_fuel_waste = sum(p.fuel_waste_pct for p in profiles) / total_drivers if profiles else 0.0
    fleet_fuel_savings = min(avg_fuel_waste * 0.8, 25.0)  # 80% of waste is recoverable
    
    return FleetCoachingSummary(
        total_drivers=total_drivers,
        needs_attention=needs_attention,
        on_track=on_track,
        improved=improved,
        average_score=average_score,
        best_improved=best_improved,
        worst_performers=worst_performers,
        fleet_fuel_savings_potential=fleet_fuel_savings,
    )


def acknowledge_coaching(driver_id: str) -> bool:
    """Mark coaching as acknowledged for a driver."""
    _acknowledgments[driver_id] = True
    return True