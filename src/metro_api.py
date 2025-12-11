"""
Metro Transit API Client
Handles all interactions with the Metro Transit NexTrip API.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timezone


class MetroTransitAPI:
    """Client for Metro Transit NexTrip API v2."""

    def __init__(self, base_url: str = "https://svc.metrotransit.org/nextrip", timeout: int = 10):
        """
        Initialize the Metro Transit API client.

        Args:
            base_url: Base URL for the Metro Transit API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout

    def get_departures(self, stop_id: str) -> List[Dict]:
        """
        Get all upcoming departures for a specific stop.

        Args:
            stop_id: The stop ID to query

        Returns:
            List of departure dictionaries

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/{stop_id}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            departures = data.get('departures', [])

            return departures

        except requests.exceptions.Timeout:
            raise Exception(f"Metro Transit API request timed out for stop {stop_id}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Metro Transit API request failed for stop {stop_id}: {e}")

    def filter_departures_by_route(
        self,
        departures: List[Dict],
        route_id: str,
        direction_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter departures by route ID and optionally by direction.

        Args:
            departures: List of all departures
            route_id: Route ID to filter by
            direction_id: Optional direction ID to filter by

        Returns:
            Filtered list of departures
        """
        filtered = [
            d for d in departures
            if str(d.get('route_id', '')) == str(route_id)
        ]

        if direction_id is not None:
            filtered = [
                d for d in filtered
                if str(d.get('direction_id', '')) == str(direction_id)
            ]

        return filtered

    @staticmethod
    def parse_departure_time(departure: Dict) -> datetime:
        """
        Parse the departure time from a departure dictionary.

        Args:
            departure: Departure dictionary from API

        Returns:
            datetime object in UTC timezone
        """
        # The API returns Unix timestamp in the 'departure_time' field
        timestamp = departure.get('departure_time')

        if timestamp:
            # Convert Unix timestamp to datetime (UTC)
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        else:
            raise ValueError("No departure_time found in departure data")

    @staticmethod
    def is_real_time(departure: Dict) -> bool:
        """
        Check if the departure time is real-time (vs scheduled).

        Args:
            departure: Departure dictionary from API

        Returns:
            True if real-time, False if scheduled
        """
        return departure.get('actual', False)

    @staticmethod
    def format_departure(departure: Dict) -> str:
        """
        Format a departure for display.

        Args:
            departure: Departure dictionary from API

        Returns:
            Formatted string representation
        """
        route = departure.get('route_short_name', 'Unknown')
        description = departure.get('description', 'Unknown')
        departure_text = departure.get('departure_text', 'N/A')
        actual = departure.get('actual', False)
        status = "Real-time" if actual else "Scheduled"

        return f"{route} to {description} - Departs: {departure_text} ({status})"
