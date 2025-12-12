# Metro Transit Pings 🚌

An automated bus alert system that monitors Metro Transit Minneapolis departures and sends timely Telegram notifications so you never miss your bus. Running entirely on GitHub Actions (no server needed), it checks real-time bus data every 5 minutes during your configured schedule and alerts you 15 minutes before you need to leave.

Features smart timing calculations based on your walking distance, multi-route monitoring, duplicate prevention, delay notifications, and pause/resume controls. Perfect for commuters with predictable schedules who want forceful reminders without constantly checking transit apps.

## How It Works

**GitHub Actions** runs every 5 minutes during your active timeframe (8:00-9:10 AM weekdays), fetches **real-time data** from Metro Transit API for your configured routes. **Calculates when to alert** based on:
   - Bus departure time
   - Your walking time to the stop (3 minutes)
   - Advance notice period (15 minutes)

**Sends Telegram notification** when it's time to head out. **Tracks sent alerts** to prevent duplicates, *mMonitors for delays** and sends updates if buses are running late.

## Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/qu-genesis/metro_transit_pings.git
cd metro_transit_pings
```

### 2. Install dependencies (for local testing)

```bash
pip install -r requirements.txt
```

### 3. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID

### 4. Configure your routes (if needed)

Edit [config.yaml](config.yaml) to adjust:
- Your bus routes and stops
- Active days and time window
- Walking time and advance notice

### 5. Push to GitHub

```bash
git add .
git commit -m "Set up bus alert system"
git push
```

### 6. Enable GitHub Actions

Go to your repository → Actions tab → Enable workflows

## Testing Locally

### Test API Connection

```bash
python test_api.py
```

This will verify that the Metro Transit API is accessible and show upcoming departures.

### Test Telegram Bot

If you want the alert to send through telegram, register a telegram bot token and telegram chat id from @botfather in Telegram.

```bash
python -c "from src.notifier import TelegramNotifier; import os; os.environ['TELEGRAM_BOT_TOKEN']='YOUR_TOKEN'; os.environ['TELEGRAM_CHAT_ID']='YOUR_CHAT_ID'; TelegramNotifier().send_test_message()"
```

Replace `YOUR_TOKEN` and `YOUR_CHAT_ID` with your actual values.

### Test Full System

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Run the main script
python main.py
```

## Configuration

See [config.yaml](config.yaml) for all available options:

- `walking_time_minutes`: Time from my residence to the bus stop
- `advance_notice_minutes`: How long it takes me to get ready
- `active_days`: Which days to monitor (0=Monday, 6=Sunday)
- `active_timeframe`: Time window for monitoring
- `routes`: Your bus routes, stops, and directions
- `alerts`: Minimum delay (minutes) to trigger delay alerts

## Project Structure

```
metro_transit_pings/
├── config.yaml              # Configuration file
├── main.py                  # Main entry point
├── test_api.py              # API testing script
├── requirements.txt         # Python dependencies
├── src/
│   ├── metro_api.py         # Metro Transit API client
│   ├── alert_logic.py       # Alert calculation logic
│   ├── notifier.py          # Telegram notification sender
│   └── state_manager.py     # State tracking for duplicates
├── .github/
│   └── workflows/
│       └── bus-alert.yml    # GitHub Actions workflow
└── alert_state.json         # State file (created at runtime)
```

## GitHub Actions Schedule

The workflow runs:
- **Every 5 minutes** from 2:00-4:15 PM UTC
- This covers 8:00-9:10 AM Central Time (both CDT and CST)
- **Monday-Friday only**

You can also trigger it manually from the Actions tab for testing. 

## Credits

Built using:
- [Metro Transit NexTrip API](https://svc.metrotransit.org/swagger/index.html)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [GitHub Actions](https://github.com/features/actions)