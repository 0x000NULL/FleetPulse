"""Safety scoring service — per-vehicle scores, trends, risk ranking."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from geotab_client import GeotabClient
from models import SafetyBreakdown, TrendDirection, VehicleSafetyScore

# Exception rule keywords → category mapping (Geotab built-in rule names)
_CATEGORY_KEYWORDS = {
    "speeding": ["speed", "posted"],
    "harsh_braking": ["hard brake", "harsh brake", "deceleration"],
    "harsh_acceleration": ["harsh accel", "hard accel", "acceleration"],
    "harsh_cornering": ["corner", "turning"],
}


def _categorize_event(rule_name: str) -> str | None:
    lower = rule_name.lower()
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return cat
    return None


def _compute_score(breakdown: SafetyBreakdown) -> float:
    """Score 0-100: starts at 100, deducts for each incident type."""
    total = (
        breakdown.speeding * 3
        + breakdown.harsh_braking * 4
        + breakdown.harsh_acceleration * 2
        + breakdown.harsh_cornering * 2
    )
    return max(0.0, round(100 - total, 1))


def get_safety_scores(days: int = 7) -> list[VehicleSafetyScore]:
    client = GeotabClient.get()
    devices = client.get_devices()
    device_map = {d["id"]: d.get("name", "Unknown") for d in devices}

    now = datetime.now(timezone.utc)
    events = client.get_exception_events(now - timedelta(days=days), now)

    # Also fetch prior period for trend
    prior_events = client.get_exception_events(
        now - timedelta(days=days * 2), now - timedelta(days=days)
    )

    def _build_breakdown(evts: list[dict[str, Any]]) -> dict[str, SafetyBreakdown]:
        per_vehicle: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for e in evts:
            dev_id = e.get("device", {}).get("id")
            rule_name = e.get("rule", {}).get("name", "")
            cat = _categorize_event(rule_name)
            if dev_id and cat:
                per_vehicle[dev_id][cat] += 1
        return {
            vid: SafetyBreakdown(**counts) for vid, counts in per_vehicle.items()
        }

    current = _build_breakdown(events)
    prior = _build_breakdown(prior_events)

    results: list[VehicleSafetyScore] = []
    for vid, name in device_map.items():
        bd = current.get(vid, SafetyBreakdown())
        score_now = _compute_score(bd)
        bd_prior = prior.get(vid, SafetyBreakdown())
        score_prior = _compute_score(bd_prior)

        if score_now > score_prior + 3:
            trend = TrendDirection.IMPROVING
        elif score_now < score_prior - 3:
            trend = TrendDirection.DECLINING
        else:
            trend = TrendDirection.STABLE

        total_events = bd.speeding + bd.harsh_braking + bd.harsh_acceleration + bd.harsh_cornering
        results.append(
            VehicleSafetyScore(
                vehicle_id=vid,
                vehicle_name=name,
                score=score_now,
                breakdown=bd,
                trend=trend,
                event_count=total_events,
            )
        )

    results.sort(key=lambda x: x.score)  # worst first for risk ranking
    return results
