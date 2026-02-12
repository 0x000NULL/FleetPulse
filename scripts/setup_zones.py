#!/usr/bin/env python3
"""Create geofence zones in Geotab for 8 Budget Rent a Car Las Vegas locations."""

import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from geotab_client import GeotabClient

LOCATIONS = [
    ("W Sahara", 36.1445, -115.1787),
    ("Golden Nugget", 36.1707, -115.1440),
    ("Center Strip", 36.1167, -115.1723),
    ("Tropicana", 36.1021, -115.1724),
    ("LAS Airport", 36.0831, -115.1523),
    ("Gibson", 36.0627, -115.1180),
    ("Henderson Executive", 35.9728, -115.1344),
    ("Losee", 36.2144, -115.1250),
]

RADIUS_M = 200
NUM_POINTS = 24  # circle approximation


def circle_points(lat: float, lon: float, radius_m: float, n: int) -> list[dict]:
    """Generate n points forming a circle of radius_m around (lat, lon)."""
    points = []
    r_lat = radius_m / 111_320
    r_lon = radius_m / (111_320 * math.cos(math.radians(lat)))
    for i in range(n):
        angle = 2 * math.pi * i / n
        points.append({
            "x": round(lon + r_lon * math.cos(angle), 6),
            "y": round(lat + r_lat * math.sin(angle), 6),
        })
    points.append(points[0])  # close the polygon
    return points


def main():
    client = GeotabClient.get()
    print(f"Authenticated to {client.database}@{client.server}")

    for name, lat, lon in LOCATIONS:
        zone_name = f"Budget - {name}"
        pts = circle_points(lat, lon, RADIUS_M, NUM_POINTS)
        zone = {
            "name": zone_name,
            "externalReference": f"fleetpulse_{name.lower().replace(' ', '_')}",
            "mustIdentifyStops": True,
            "displayed": True,
            "activeFrom": "2020-01-01T00:00:00Z",
            "activeTo": "2099-12-31T23:59:59Z",
            "zoneTypes": [{"id": "ZoneTypeCustomerId"}],
            "groups": [{"id": "GroupCompanyId"}],
            "points": pts,
        }
        try:
            zone_id = client.add_zone(zone)
            print(f"  ✅ Created zone '{zone_name}' → {zone_id}")
        except Exception as e:
            print(f"  ⚠️  Zone '{zone_name}': {e}")

    print("\nDone! All 8 Budget locations configured.")


if __name__ == "__main__":
    main()
