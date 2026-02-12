#!/usr/bin/env python3
"""Seed driver profiles into Geotab for FleetPulse demo."""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from geotab_client import GeotabClient

DRIVERS = [
    {"firstName": "Marcus", "lastName": "Rivera", "name": "Marcus Rivera"},
    {"firstName": "Aisha", "lastName": "Patel", "name": "Aisha Patel"},
    {"firstName": "Jake", "lastName": "Thompson", "name": "Jake Thompson"},
    {"firstName": "Sofia", "lastName": "Chen", "name": "Sofia Chen"},
    {"firstName": "DeShawn", "lastName": "Williams", "name": "DeShawn Williams"},
    {"firstName": "Emily", "lastName": "Nakamura", "name": "Emily Nakamura"},
    {"firstName": "Carlos", "lastName": "Gutierrez", "name": "Carlos Gutierrez"},
    {"firstName": "Rachel", "lastName": "Kim", "name": "Rachel Kim"},
]


def main():
    client = GeotabClient.get()
    api = client.api
    print(f"Authenticated to {client.database}@{client.server}")

    for d in DRIVERS:
        try:
            driver_id = api.add("Driver", {
                "firstName": d["firstName"],
                "lastName": d["lastName"],
                "name": d["name"],
                "securityGroups": [{"id": "GroupEverythingSecurityId"}],
            })
            print(f"  ✅ Created driver '{d['name']}' → {driver_id}")
        except Exception as e:
            print(f"  ⚠️  Driver '{d['name']}': {e}")

    print("\nDone! Driver profiles seeded.")


if __name__ == "__main__":
    main()
