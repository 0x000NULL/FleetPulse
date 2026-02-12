#!/usr/bin/env python3
"""Seed driver profiles into Geotab for FleetPulse demo."""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from geotab_client import GeotabClient

DRIVERS = [
    {"firstName": "Marcus", "lastName": "Rivera", "name": "marcus.rivera@fleetpulse"},
    {"firstName": "Aisha", "lastName": "Patel", "name": "aisha.patel@fleetpulse"},
    {"firstName": "Jake", "lastName": "Thompson", "name": "jake.thompson@fleetpulse"},
    {"firstName": "Sofia", "lastName": "Chen", "name": "sofia.chen@fleetpulse"},
    {"firstName": "DeShawn", "lastName": "Williams", "name": "deshawn.williams@fleetpulse"},
    {"firstName": "Emily", "lastName": "Nakamura", "name": "emily.nakamura@fleetpulse"},
    {"firstName": "Carlos", "lastName": "Gutierrez", "name": "carlos.gutierrez@fleetpulse"},
    {"firstName": "Rachel", "lastName": "Kim", "name": "rachel.kim@fleetpulse"},
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
                "password": "FleetPulse2026!",
                "securityGroups": [{"id": "GroupEverythingSecurityId"}],
                "companyGroups": [{"id": "GroupCompanyId"}],
            })
            print(f"  ✅ Created driver '{d['name']}' → {driver_id}")
        except Exception as e:
            print(f"  ⚠️  Driver '{d['name']}': {e}")

    print("\nDone! Driver profiles seeded.")


if __name__ == "__main__":
    main()
