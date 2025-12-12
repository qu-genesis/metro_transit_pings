#!/usr/bin/env python3
"""
Metro Transit Pings - Main Entry Point
Checks bus times and sends alerts via Telegram.
"""

import os
import sys
import yaml
import json
from datetime import datetime, timezone
from pathlib import Path
import pytz

from src.metro_api import MetroTransitAPI
from src.alert_logic import AlertCalculator
from src.notifier import TelegramNotifier
from src.state_manager import StateManager


def is_paused() -> bool:
    """
    Check if alerts are currently paused.

    Returns:
        True if paused, False otherwise
    """
    pause_file = Path(".pause_state.json")

    if not pause_file.exists():
        return False

    try:
        with open(pause_file, 'r') as f:
            state = json.load(f)
            return state.get('paused', False)
    except (json.JSONDecodeError, IOError):
        return False


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def is_active_time(config: dict, current_time: datetime) -> bool:
    """
    Check if current time is within the active monitoring window.

    Args:
        config: Configuration dictionary
        current_time: Current time (UTC)

    Returns:
        True if within active window, False otherwise
    """
    prefs = config['user_preferences']
    tz = pytz.timezone(prefs['timezone'])

    # Convert current time to local timezone
    local_time = current_time.astimezone(tz)

    # Check if today is an active day (0=Monday, 6=Sunday)
    if local_time.weekday() not in prefs['active_days']:
        print(f"Today ({local_time.strftime('%A')}) is not an active day")
        return False

    # Parse active timeframe
    start_str = prefs['active_timeframe']['start']
    end_str = prefs['active_timeframe']['end']

    start_hour, start_min = map(int, start_str.split(':'))
    end_hour, end_min = map(int, end_str.split(':'))

    current_hour = local_time.hour
    current_min = local_time.minute

    # Convert to minutes since midnight for easier comparison
    current_minutes = current_hour * 60 + current_min
    start_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min

    if not (start_minutes <= current_minutes <= end_minutes):
        print(f"Current time {local_time.strftime('%I:%M %p')} is outside active window ({start_str}-{end_str})")
        return False

    return True


def main():
    """Main execution function."""
    print("=" * 60)
    print("Metro Transit Pings - Bus Alert System")
    print("=" * 60)

    # Load configuration
    config = load_config()

    # Get current time
    current_time = datetime.now(timezone.utc)
    tz = pytz.timezone(config['user_preferences']['timezone'])
    local_time = current_time.astimezone(tz)
    print(f"Current time: {local_time.strftime('%A, %B %d, %Y %I:%M %p %Z')}")
    print()

    # Check if we should run
    if not is_active_time(config, current_time):
        print("Outside active monitoring window. Exiting.")
        return

    # Check if alerts are paused
    if is_paused():
        print("⏸️  Alerts are currently paused. Send /start to resume.")
        print("Exiting.")
        return

    # Initialize components
    print("Initializing components...")
    api = MetroTransitAPI(
        base_url=config['api']['base_url'],
        timeout=config['api']['timeout_seconds']
    )

    alert_calc = AlertCalculator(
        walking_time_minutes=config['user_preferences']['walking_time_minutes'],
        advance_notice_minutes=config['user_preferences']['advance_notice_minutes'],
        timezone_str=config['user_preferences']['timezone']
    )

    notifier = TelegramNotifier()
    state = StateManager()

    # Update last run time
    state.update_last_run(current_time)

    # Clean up old state entries
    state.cleanup_old_entries(max_age_hours=2)

    print("Components initialized.\n")

    # Get all routes to check
    routes = config['routes']
    all_alerts_to_send = []
    all_delay_updates = []

    for route_config in routes:
        route_id = str(route_config['route_id'])
        stop_id = str(route_config['stop_id'])
        description = route_config['description']

        print(f"Checking {description}...")

        try:
            # Fetch departures from API
            all_departures = api.get_departures(stop_id)

            # Filter for this route
            route_departures = api.filter_departures_by_route(
                all_departures,
                route_id
            )

            if not route_departures:
                print(f"  No departures found for {description}")
                continue

            print(f"  Found {len(route_departures)} departure(s)")

            # Check each departure
            for departure in route_departures:
                trip_id = str(departure.get('trip_id', ''))
                departure_time = api.parse_departure_time(departure)

                # Check if departure is relevant (not too far in future)
                if not alert_calc.is_departure_relevant(departure_time, current_time):
                    continue

                # Calculate times
                leave_time = alert_calc.calculate_leave_time(departure_time)
                should_alert = alert_calc.should_alert_now(departure_time, current_time)

                # Check if we've already alerted for this departure
                already_alerted = state.has_alerted(route_id, trip_id, stop_id)

                if should_alert and not already_alerted:
                    # This is a new alert to send
                    print(f"    ✓ Alert needed: {api.format_departure(departure)}")

                    # Add calculated times to departure
                    departure['departure_datetime'] = departure_time
                    departure['leave_datetime'] = leave_time
                    all_alerts_to_send.append(departure)

                    # Record the alert (we'll actually send it later)
                    state.record_alert(route_id, trip_id, stop_id, departure_time, current_time)

                elif already_alerted:
                    # Check for delays
                    tracked = state.get_tracked_departure(route_id, trip_id, stop_id)

                    if tracked:
                        original_time = datetime.fromisoformat(tracked['original_departure_time'])
                        delay_minutes = alert_calc.calculate_delay(original_time, departure_time)

                        # If delayed by more than threshold and we haven't sent update yet
                        delay_threshold = config['alerts']['delay_threshold_minutes']
                        if delay_minutes >= delay_threshold and not state.has_sent_delay_update(route_id, trip_id, stop_id):
                            print(f"    ⚠️  Delay detected: {delay_minutes} min - {api.format_departure(departure)}")

                            all_delay_updates.append({
                                'route': departure.get('route_short_name', route_id),
                                'description': departure.get('description', 'Unknown'),
                                'original_time': original_time,
                                'new_time': departure_time,
                                'delay_minutes': delay_minutes
                            })

                            # Record the delay update
                            state.record_delay_update(route_id, trip_id, stop_id, departure_time)

        except Exception as e:
            print(f"  Error checking {description}: {e}")
            continue

    print()

    # Deduplicate alerts by departure time and route
    # (API sometimes returns duplicate entries for same departure)
    if all_alerts_to_send:
        seen = {}
        deduped_alerts = []
        for alert in all_alerts_to_send:
            key = (alert.get('route_id'), alert.get('departure_time'))
            if key not in seen:
                seen[key] = True
                deduped_alerts.append(alert)
        all_alerts_to_send = deduped_alerts

    # Send alerts
    if all_alerts_to_send:
        print(f"Sending alert for {len(all_alerts_to_send)} departure(s)...")
        success = notifier.send_bus_alert(all_alerts_to_send, alert_calc, current_time)

        if success:
            print("  ✓ Alert sent successfully!")
        else:
            print("  ✗ Failed to send alert")
    else:
        # Calculate when next alert might be sent
        advance_min = config['user_preferences']['advance_notice_minutes']
        walking_min = config['user_preferences']['walking_time_minutes']
        total_buffer = advance_min + walking_min

        print(f"No alerts to send at this time.")
        print(f"ℹ️  Alerts are sent {advance_min} minutes before you need to leave.")
        print(f"   (Buses departing within the next ~{total_buffer} minutes would trigger alerts)")

    # Send delay updates
    if all_delay_updates:
        print(f"\nSending {len(all_delay_updates)} delay update(s)...")

        for delay in all_delay_updates:
            success = notifier.send_delay_alert(
                route=delay['route'],
                description=delay['description'],
                original_time=delay['original_time'],
                new_time=delay['new_time'],
                delay_minutes=delay['delay_minutes'],
                alert_calculator=alert_calc,
                current_time=current_time
            )

            if success:
                print(f"  ✓ Delay update sent for {delay['route']}")
            else:
                print(f"  ✗ Failed to send delay update for {delay['route']}")

    print("\n" + "=" * 60)
    print("Run complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
