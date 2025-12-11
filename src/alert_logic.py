"""
Alert Logic Engine
Calculates when to send alerts based on bus departure times and user preferences.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
import pytz


class AlertCalculator:
    """Calculates when alerts should be sent for bus departures."""

    def __init__(
        self,
        walking_time_minutes: int,
        advance_notice_minutes: int,
        timezone_str: str = "America/Chicago"
    ):
        """
        Initialize the alert calculator.

        Args:
            walking_time_minutes: Time to walk from home to bus stop
            advance_notice_minutes: How far in advance to alert (e.g., 15 minutes)
            timezone_str: Timezone string for local time conversion
        """
        self.walking_time_minutes = walking_time_minutes
        self.advance_notice_minutes = advance_notice_minutes
        self.timezone = pytz.timezone(timezone_str)

    def calculate_leave_time(self, departure_time: datetime) -> datetime:
        """
        Calculate when the user needs to leave home.

        Args:
            departure_time: When the bus departs (UTC)

        Returns:
            When the user should leave home (UTC)
        """
        # Leave time = departure time - walking time
        leave_time = departure_time - timedelta(minutes=self.walking_time_minutes)
        return leave_time

    def calculate_alert_time(self, departure_time: datetime) -> datetime:
        """
        Calculate when to send the alert.

        Args:
            departure_time: When the bus departs (UTC)

        Returns:
            When to send the alert (UTC)
        """
        leave_time = self.calculate_leave_time(departure_time)
        # Alert time = leave time - advance notice
        alert_time = leave_time - timedelta(minutes=self.advance_notice_minutes)
        return alert_time

    def should_alert_now(
        self,
        departure_time: datetime,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Determine if an alert should be sent now.

        Args:
            departure_time: When the bus departs (UTC)
            current_time: Current time (UTC). If None, uses datetime.now(UTC)

        Returns:
            True if alert should be sent now, False otherwise
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        alert_time = self.calculate_alert_time(departure_time)
        leave_time = self.calculate_leave_time(departure_time)

        # Alert should be sent if:
        # 1. Current time is past the alert time
        # 2. Current time is before the leave time (not too late)
        return alert_time <= current_time <= leave_time

    def is_departure_relevant(
        self,
        departure_time: datetime,
        current_time: Optional[datetime] = None,
        max_wait_minutes: int = 60
    ) -> bool:
        """
        Check if a departure is relevant (not too soon, not too far away).

        Args:
            departure_time: When the bus departs (UTC)
            current_time: Current time (UTC). If None, uses datetime.now(UTC)
            max_wait_minutes: Maximum wait time to consider (default 60 min)

        Returns:
            True if departure is relevant, False otherwise
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        alert_time = self.calculate_alert_time(departure_time)
        time_until_alert = (alert_time - current_time).total_seconds() / 60

        # Departure is relevant if:
        # 1. Alert time is in the future (or very recent past - within alert window)
        # 2. Not too far in the future (within max_wait_minutes)
        return -self.advance_notice_minutes <= time_until_alert <= max_wait_minutes

    def format_time_local(self, dt: datetime) -> str:
        """
        Format a datetime in local timezone.

        Args:
            dt: datetime object (any timezone)

        Returns:
            Formatted string in local timezone (e.g., "8:45 AM")
        """
        local_time = dt.astimezone(self.timezone)
        return local_time.strftime("%I:%M %p").lstrip("0")

    def minutes_until(self, future_time: datetime, current_time: Optional[datetime] = None) -> int:
        """
        Calculate minutes until a future time.

        Args:
            future_time: Future datetime
            current_time: Current time. If None, uses datetime.now(UTC)

        Returns:
            Number of minutes (rounded)
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        delta = future_time - current_time
        return round(delta.total_seconds() / 60)

    def calculate_delay(
        self,
        original_departure_time: datetime,
        current_departure_time: datetime
    ) -> int:
        """
        Calculate delay in minutes between original and current departure times.

        Args:
            original_departure_time: Original predicted departure time
            current_departure_time: Current predicted departure time

        Returns:
            Delay in minutes (positive = late, negative = early)
        """
        delta = current_departure_time - original_departure_time
        return round(delta.total_seconds() / 60)
