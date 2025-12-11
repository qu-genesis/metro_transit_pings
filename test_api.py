#!/usr/bin/env python3
"""
Quick test script to verify Metro Transit API access with your specific routes.
Run this first to make sure we can fetch bus data!
"""

import requests
import json
from datetime import datetime

# Your configuration
STOP_ID = "50195"
ROUTES = [
    {"route": "17", "direction": "2", "name": "Route 17 Eastbound"},
    {"route": "925", "direction": "4", "name": "E Line Northbound"}  # E Line = Route 925
]

BASE_URL = "https://svc.metrotransit.org/nextrip"


def test_api():
    """Test the Metro Transit API with your routes."""
    print("=" * 60)
    print("Metro Transit API Test")
    print("=" * 60)
    print(f"\nTesting Stop ID: {STOP_ID}")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}\n")

    # Use the simpler endpoint: /nextrip/{stop_id}
    # This gets ALL departures at the stop, then we filter by route
    url = f"{BASE_URL}/{STOP_ID}"

    try:
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract the departures list from the response
        all_departures = data.get('departures', [])

        if not all_departures:
            print("  ⚠️  No upcoming departures found at this stop")
        else:
            print(f"  ✓ Found {len(all_departures)} total upcoming departure(s)\n")

            # Filter and display for each configured route
            for route_info in ROUTES:
                route_id = route_info["route"]
                name = route_info["name"]

                print(f"\n--- {name} ---")

                # Filter departures for this route
                route_departures = [
                    d for d in all_departures
                    if isinstance(d, dict) and str(d.get('route_id', '')) == route_id
                ]

                if not route_departures:
                    print("  ⚠️  No departures found for this route")
                else:
                    print(f"  ✓ Found {len(route_departures)} departure(s):\n")

                    for i, dep in enumerate(route_departures[:3], 1):  # Show first 3
                        actual = dep.get('actual', False)
                        departure_text = dep.get('departure_text', 'N/A')
                        departure_time = dep.get('departure_time', 'N/A')
                        description = dep.get('description', 'Unknown')
                        route_short_name = dep.get('route_short_name', 'N/A')

                        status = "Real-time" if actual else "Scheduled"

                        print(f"    {i}. {route_short_name} - {description}")
                        print(f"       Departs: {departure_text}")
                        print(f"       Time: {departure_time}")
                        print(f"       Status: {status}")
                        print()

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error: {e}")
        print(f"\nFull response if available:")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Body: {e.response.text[:500]}")
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON Error: {e}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_api()
