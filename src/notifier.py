"""
Telegram Notifier
Sends alerts via Telegram bot.
"""

import os
import requests
from typing import Optional, List, Dict
from datetime import datetime


class TelegramNotifier:
    """Sends notifications via Telegram."""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize the Telegram notifier.

        Args:
            bot_token: Telegram bot token (if None, reads from TELEGRAM_BOT_TOKEN env var)
            chat_id: Telegram chat ID (if None, reads from TELEGRAM_CHAT_ID env var)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token:
            raise ValueError("Telegram bot token not provided")
        if not self.chat_id:
            raise ValueError("Telegram chat ID not provided")

        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message via Telegram.

        Args:
            text: Message text to send
            parse_mode: Telegram parse mode (Markdown or HTML)

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.api_url}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def send_bus_alert(
        self,
        departures: List[Dict],
        alert_calculator,
        current_time: datetime
    ) -> bool:
        """
        Send a bus alert for multiple departures.

        Args:
            departures: List of departure dictionaries with calculated times
            alert_calculator: AlertCalculator instance for time formatting
            current_time: Current time (UTC)

        Returns:
            True if successful, False otherwise
        """
        if not departures:
            return False

        message_lines = ["🚌 *Time to head out!*\n"]

        for dep in departures:
            route = dep.get('route_short_name', 'Unknown')
            description = dep.get('description', 'Unknown')
            departure_time = dep.get('departure_datetime')
            leave_time = dep.get('leave_datetime')

            if not departure_time or not leave_time:
                continue

            depart_local = alert_calculator.format_time_local(departure_time)
            leave_local = alert_calculator.format_time_local(leave_time)

            minutes_until_depart = alert_calculator.minutes_until(departure_time, current_time)
            minutes_until_leave = alert_calculator.minutes_until(leave_time, current_time)

            message_lines.append(f"*{route}* to {description}")
            message_lines.append(f"🚏 Departs: {depart_local} (in {minutes_until_depart} min)")
            message_lines.append(f"🚶 Leave by: {leave_local} (in {minutes_until_leave} min)")
            message_lines.append("")

        message = "\n".join(message_lines)
        return self.send_message(message)

    def send_delay_alert(
        self,
        route: str,
        description: str,
        original_time: datetime,
        new_time: datetime,
        delay_minutes: int,
        alert_calculator,
        current_time: datetime
    ) -> bool:
        """
        Send a delay notification.

        Args:
            route: Route short name
            description: Route description
            original_time: Original departure time
            new_time: New departure time
            delay_minutes: Minutes of delay
            alert_calculator: AlertCalculator instance for time formatting
            current_time: Current time

        Returns:
            True if successful, False otherwise
        """
        original_local = alert_calculator.format_time_local(original_time)
        new_local = alert_calculator.format_time_local(new_time)

        new_leave_time = alert_calculator.calculate_leave_time(new_time)
        new_leave_local = alert_calculator.format_time_local(new_leave_time)
        minutes_until_leave = alert_calculator.minutes_until(new_leave_time, current_time)

        message = f"""⚠️ *Bus Update - {route} Delayed*

Original: {original_local}
Now: {new_local} (+{delay_minutes} min delay)

🚶 New leave time: {new_leave_local} (in {minutes_until_leave} min)"""

        return self.send_message(message)

    def send_test_message(self) -> bool:
        """
        Send a test message to verify the bot is working.

        Returns:
            True if successful, False otherwise
        """
        message = "✅ Metro Transit Pings test message - Bot is working!"
        return self.send_message(message)
