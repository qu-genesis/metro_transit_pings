"""
State Manager
Tracks sent alerts and departure states to prevent duplicates and detect delays.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional


class StateManager:
    """Manages state for tracking sent alerts and detecting delays."""

    def __init__(self, state_file: str = "alert_state.json"):
        """
        Initialize the state manager.

        Args:
            state_file: Path to the JSON file for storing state
        """
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """
        Load state from file.

        Returns:
            State dictionary
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load state from {self.state_file}, starting fresh")
                return self._new_state()
        else:
            return self._new_state()

    def _new_state(self) -> Dict:
        """Create a new empty state."""
        return {
            "last_run": None,
            "tracked_departures": []
        }

    def _save_state(self):
        """Save state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save state to {self.state_file}: {e}")

    def update_last_run(self, run_time: Optional[datetime] = None):
        """
        Update the last run timestamp.

        Args:
            run_time: Time of the run (UTC). If None, uses current time.
        """
        if run_time is None:
            run_time = datetime.now(timezone.utc)

        self.state["last_run"] = run_time.isoformat()
        self._save_state()

    def _create_departure_key(self, route_id: str, trip_id: str, stop_id: str) -> str:
        """
        Create a unique key for a departure.

        Args:
            route_id: Route ID
            trip_id: Trip ID
            stop_id: Stop ID

        Returns:
            Unique departure key
        """
        return f"{route_id}_{trip_id}_{stop_id}"

    def has_alerted(self, route_id: str, trip_id: str, stop_id: str) -> bool:
        """
        Check if we've already sent an initial alert for this departure.

        Args:
            route_id: Route ID
            trip_id: Trip ID
            stop_id: Stop ID

        Returns:
            True if already alerted, False otherwise
        """
        key = self._create_departure_key(route_id, trip_id, stop_id)

        for dep in self.state["tracked_departures"]:
            if dep.get("key") == key and dep.get("initial_alert_sent"):
                return True

        return False

    def has_sent_delay_update(self, route_id: str, trip_id: str, stop_id: str) -> bool:
        """
        Check if we've already sent a delay update for this departure.

        Args:
            route_id: Route ID
            trip_id: Trip ID
            stop_id: Stop ID

        Returns:
            True if delay update already sent, False otherwise
        """
        key = self._create_departure_key(route_id, trip_id, stop_id)

        for dep in self.state["tracked_departures"]:
            if dep.get("key") == key:
                return dep.get("delay_update_sent", False)

        return False

    def record_alert(
        self,
        route_id: str,
        trip_id: str,
        stop_id: str,
        departure_time: datetime,
        alert_time: Optional[datetime] = None
    ):
        """
        Record that an initial alert has been sent for a departure.

        Args:
            route_id: Route ID
            trip_id: Trip ID
            stop_id: Stop ID
            departure_time: Departure time (UTC)
            alert_time: When alert was sent (UTC). If None, uses current time.
        """
        if alert_time is None:
            alert_time = datetime.now(timezone.utc)

        key = self._create_departure_key(route_id, trip_id, stop_id)

        # Check if already exists
        for dep in self.state["tracked_departures"]:
            if dep.get("key") == key:
                dep["initial_alert_sent"] = True
                dep["initial_alert_time"] = alert_time.isoformat()
                dep["original_departure_time"] = departure_time.isoformat()
                dep["current_departure_time"] = departure_time.isoformat()
                self._save_state()
                return

        # Add new tracking entry
        self.state["tracked_departures"].append({
            "key": key,
            "route_id": str(route_id),
            "trip_id": str(trip_id),
            "stop_id": str(stop_id),
            "original_departure_time": departure_time.isoformat(),
            "current_departure_time": departure_time.isoformat(),
            "initial_alert_sent": True,
            "initial_alert_time": alert_time.isoformat(),
            "delay_update_sent": False
        })

        self._save_state()

    def record_delay_update(self, route_id: str, trip_id: str, stop_id: str, new_departure_time: datetime):
        """
        Record that a delay update has been sent for a departure.

        Args:
            route_id: Route ID
            trip_id: Trip ID
            stop_id: Stop ID
            new_departure_time: New departure time (UTC)
        """
        key = self._create_departure_key(route_id, trip_id, stop_id)

        for dep in self.state["tracked_departures"]:
            if dep.get("key") == key:
                dep["delay_update_sent"] = True
                dep["current_departure_time"] = new_departure_time.isoformat()
                dep["delay_update_time"] = datetime.now(timezone.utc).isoformat()
                self._save_state()
                return

    def get_tracked_departure(self, route_id: str, trip_id: str, stop_id: str) -> Optional[Dict]:
        """
        Get the tracked state for a departure.

        Args:
            route_id: Route ID
            trip_id: Trip ID
            stop_id: Stop ID

        Returns:
            Tracked departure dict or None if not found
        """
        key = self._create_departure_key(route_id, trip_id, stop_id)

        for dep in self.state["tracked_departures"]:
            if dep.get("key") == key:
                return dep

        return None

    def cleanup_old_entries(self, max_age_hours: int = 2):
        """
        Remove old tracking entries to prevent the state file from growing too large.

        Args:
            max_age_hours: Maximum age of entries to keep (default 2 hours)
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        self.state["tracked_departures"] = [
            dep for dep in self.state["tracked_departures"]
            if datetime.fromisoformat(dep.get("original_departure_time", "1970-01-01T00:00:00+00:00")) > cutoff_time
        ]

        self._save_state()
