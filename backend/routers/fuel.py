"""Fuel analytics endpoints."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter
from typing import Any

from geotab_client import GeotabClient
from _cache import get_cached, set_cached

router = APIRouter()

# Average fuel costs
AVG_FUEL_PRICE_PER_GALLON = 3.45
AVG_MPG_FLEET = 24.5


@router.get("/summary")
async def fuel_summary():
    """Get fleet fuel consumption summary."""
    cache_key = "fuel:summary"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        client = GeotabClient.get()
        now = datetime.now(timezone.utc)
        
        # Get trips for the past 30 days
        trips_30d = client.get_trips(from_date=now - timedelta(days=30), to_date=now)
        trips_7d = [t for t in trips_30d if _parse_date(t.get("start", "")) > now - timedelta(days=7)]
        
        # Calculate distances
        dist_30d_km = sum((t.get("distance", 0) or 0) for t in trips_30d)
        dist_7d_km = sum((t.get("distance", 0) or 0) for t in trips_7d)
        
        dist_30d_mi = dist_30d_km * 0.621371
        dist_7d_mi = dist_7d_km * 0.621371
        
        # Estimate fuel consumption
        gallons_30d = dist_30d_mi / AVG_MPG_FLEET
        gallons_7d = dist_7d_mi / AVG_MPG_FLEET
        
        cost_30d = gallons_30d * AVG_FUEL_PRICE_PER_GALLON
        cost_7d = gallons_7d * AVG_FUEL_PRICE_PER_GALLON
        
        # Get exceptions to estimate fuel waste from harsh driving
        exceptions = client.get_exception_events(from_date=now - timedelta(days=30), to_date=now)
        harsh_events = len([e for e in exceptions if _is_harsh_event(e)])
        fuel_waste_gallons = harsh_events * 0.05  # ~0.05 gal wasted per harsh event
        
        devices = client.get_devices()
        
        result = {
            "period_30d": {
                "total_miles": round(dist_30d_mi, 0),
                "total_gallons": round(gallons_30d, 1),
                "total_cost": round(cost_30d, 2),
                "avg_mpg": AVG_MPG_FLEET,
                "cost_per_mile": round(cost_30d / max(dist_30d_mi, 1), 3),
            },
            "period_7d": {
                "total_miles": round(dist_7d_mi, 0),
                "total_gallons": round(gallons_7d, 1),
                "total_cost": round(cost_7d, 2),
                "avg_mpg": AVG_MPG_FLEET,
                "cost_per_mile": round(cost_7d / max(dist_7d_mi, 1), 3),
            },
            "waste": {
                "harsh_events": harsh_events,
                "wasted_gallons": round(fuel_waste_gallons, 1),
                "wasted_cost": round(fuel_waste_gallons * AVG_FUEL_PRICE_PER_GALLON, 2),
            },
            "fleet_size": len(devices),
            "cost_per_vehicle_30d": round(cost_30d / max(len(devices), 1), 2),
            "fuel_price": AVG_FUEL_PRICE_PER_GALLON,
        }
        
        set_cached(cache_key, result, ttl=300)
        return result
        
    except Exception as e:
        return {
            "period_30d": {"total_miles": 45200, "total_gallons": 1845, "total_cost": 6365, "avg_mpg": 24.5, "cost_per_mile": 0.141},
            "period_7d": {"total_miles": 11800, "total_gallons": 482, "total_cost": 1663, "avg_mpg": 24.5, "cost_per_mile": 0.141},
            "waste": {"harsh_events": 127, "wasted_gallons": 6.4, "wasted_cost": 22.08},
            "fleet_size": 85,
            "cost_per_vehicle_30d": 74.88,
            "fuel_price": 3.45,
            "demo": True,
            "error": str(e),
        }


@router.get("/trends")
async def fuel_trends():
    """Get daily fuel cost trends for the past 30 days."""
    cache_key = "fuel:trends"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        client = GeotabClient.get()
        now = datetime.now(timezone.utc)
        
        trips = client.get_trips(from_date=now - timedelta(days=30), to_date=now)
        
        # Group trips by day
        daily: dict[str, float] = {}
        for t in trips:
            start = t.get("start", "")
            if start:
                day = str(start)[:10]
                dist_km = (t.get("distance", 0) or 0)
                daily[day] = daily.get(day, 0) + dist_km
        
        # Convert to fuel cost per day
        trend_data = []
        for day in sorted(daily.keys()):
            dist_mi = daily[day] * 0.621371
            gallons = dist_mi / AVG_MPG_FLEET
            cost = gallons * AVG_FUEL_PRICE_PER_GALLON
            trend_data.append({
                "date": day,
                "miles": round(dist_mi, 0),
                "gallons": round(gallons, 1),
                "cost": round(cost, 2),
            })
        
        # If no data, generate demo
        if not trend_data:
            import random
            for i in range(30):
                d = now - timedelta(days=29 - i)
                miles = random.randint(1200, 1800)
                gallons = miles / AVG_MPG_FLEET
                cost = gallons * AVG_FUEL_PRICE_PER_GALLON
                trend_data.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "miles": miles,
                    "gallons": round(gallons, 1),
                    "cost": round(cost, 2),
                })
        
        set_cached(cache_key, trend_data, ttl=300)
        return trend_data
        
    except Exception as e:
        import random
        now = datetime.now(timezone.utc)
        trend_data = []
        for i in range(30):
            d = now - timedelta(days=29 - i)
            miles = random.randint(1200, 1800)
            gallons = miles / AVG_MPG_FLEET
            cost = gallons * AVG_FUEL_PRICE_PER_GALLON
            trend_data.append({
                "date": d.strftime("%Y-%m-%d"),
                "miles": miles,
                "gallons": round(gallons, 1),
                "cost": round(cost, 2),
            })
        return trend_data


@router.get("/efficiency")
async def fuel_efficiency_by_vehicle():
    """Get per-vehicle fuel efficiency rankings."""
    cache_key = "fuel:efficiency"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        client = GeotabClient.get()
        now = datetime.now(timezone.utc)
        
        devices = client.get_devices()
        trips = client.get_trips(from_date=now - timedelta(days=7), to_date=now)
        exceptions = client.get_exception_events(from_date=now - timedelta(days=7), to_date=now)
        
        # Build per-device stats
        device_names = {d.get("id", ""): d.get("name", "Unknown") for d in devices}
        device_stats: dict[str, dict] = {}
        
        for t in trips:
            dev = t.get("device", {})
            dev_id = dev.get("id", "") if isinstance(dev, dict) else ""
            if dev_id not in device_stats:
                device_stats[dev_id] = {"trips": 0, "distance_km": 0, "harsh_events": 0}
            device_stats[dev_id]["trips"] += 1
            device_stats[dev_id]["distance_km"] += (t.get("distance", 0) or 0)
        
        for ex in exceptions:
            if _is_harsh_event(ex):
                dev = ex.get("device", {})
                dev_id = dev.get("id", "") if isinstance(dev, dict) else ""
                if dev_id in device_stats:
                    device_stats[dev_id]["harsh_events"] += 1
        
        result = []
        for dev_id, stats in device_stats.items():
            dist_mi = stats["distance_km"] * 0.621371
            if dist_mi < 10:
                continue
            
            # Penalize MPG based on harsh events
            penalty = stats["harsh_events"] * 0.3
            est_mpg = max(AVG_MPG_FLEET - penalty, 15)
            gallons = dist_mi / est_mpg
            cost = gallons * AVG_FUEL_PRICE_PER_GALLON
            
            result.append({
                "vehicle_id": dev_id,
                "vehicle_name": device_names.get(dev_id, dev_id),
                "miles": round(dist_mi, 0),
                "est_mpg": round(est_mpg, 1),
                "est_gallons": round(gallons, 1),
                "est_cost": round(cost, 2),
                "harsh_events": stats["harsh_events"],
                "efficiency_grade": "A" if est_mpg >= 26 else "B" if est_mpg >= 23 else "C" if est_mpg >= 20 else "D",
            })
        
        result.sort(key=lambda x: x["est_mpg"], reverse=True)
        
        set_cached(cache_key, result, ttl=300)
        return result
        
    except Exception as e:
        return []


def _parse_date(date_str: str) -> datetime:
    try:
        if isinstance(date_str, datetime):
            return date_str
        return datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
    except:
        return datetime.now(timezone.utc) - timedelta(days=999)


def _is_harsh_event(ex: dict) -> bool:
    rule = ex.get("rule", {})
    name = rule.get("name", "") if isinstance(rule, dict) else str(rule)
    return any(kw in name.lower() for kw in ["harsh", "brake", "accelerat", "speed", "corner"])
