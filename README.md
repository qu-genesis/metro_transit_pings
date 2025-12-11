# Metro Transit Pings 🚌

**Me go bus when?** - Automated bus departure alerts for Metro Transit Minneapolis

Never miss your bus again! This system automatically monitors Metro Transit bus arrivals and sends you timely Telegram notifications so you know exactly when to leave your apartment.

## Features

- 📱 **Telegram Alerts**: Get instant push notifications on your phone
- 🕐 **Smart Timing**: Alerts sent 15 minutes before you need to leave
- 🚌 **Multi-Route Support**: Track multiple bus routes simultaneously
- ⚠️ **Delay Notifications**: Get updates if your bus is running late
- 🤖 **Fully Automated**: Runs on GitHub Actions - no server needed!
- ⏰ **Scheduled Monitoring**: Only runs during your configured time window

## How It Works

1. **GitHub Actions** runs every 5 minutes during your active timeframe (8:00-9:10 AM weekdays)
2. **Fetches real-time data** from Metro Transit API for your configured routes
3. **Calculates when to alert** based on:
   - Bus departure time
   - Your walking time to the stop (3 minutes)
   - Advance notice period (15 minutes)
4. **Sends Telegram notification** when it's time to head out
5. **Tracks sent alerts** to prevent duplicates
6. **Monitors for delays** and sends updates if buses are running late

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

- **Walking time**: Time from your apartment to the bus stop
- **Advance notice**: How early you want to be alerted
- **Active days**: Which days to monitor (0=Monday, 6=Sunday)
- **Active timeframe**: Time window for monitoring
- **Routes**: Your bus routes, stops, and directions
- **Delay threshold**: Minimum delay (minutes) to trigger delay alerts

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

## How Alerts Work

### Initial Alert

When a bus is arriving and it's time to leave:

```
🚌 Time to head out!

17 to Blake Road
🚏 Departs: 8:45 AM (in 20 min)
🚶 Leave by: 8:42 AM (in 17 min)

E Line to Southdale
🚏 Departs: 8:48 AM (in 23 min)
🚶 Leave by: 8:45 AM (in 20 min)
```

### Delay Alert

If a bus you've been alerted about gets delayed:

```
⚠️ Bus Update - 17 Delayed

Original: 8:45 AM
Now: 8:52 AM (+7 min delay)

🚶 New leave time: 8:49 AM (in 6 min)
```

## GitHub Actions Schedule

The workflow runs:
- **Every 5 minutes** from 2:00-4:15 PM UTC
- This covers 8:00-9:10 AM Central Time (both CDT and CST)
- **Monday-Friday only**

You can also trigger it manually from the Actions tab for testing.

## Troubleshooting

### Not receiving alerts?

1. Check GitHub Actions → Workflow runs for errors
2. Verify your secrets are set correctly
3. Check that you're within the active time window
4. Run `python test_api.py` to verify API access

### Getting duplicate alerts?

The state management system should prevent this, but if it happens:
1. Check if `alert_state.json` is being persisted correctly
2. Verify the artifact upload/download is working in GitHub Actions

### Wrong timezone?

The config uses `America/Chicago` (Central Time). GitHub Actions runs in UTC, but the code handles conversion automatically.

## Credits

Built using:
- [Metro Transit NexTrip API](https://svc.metrotransit.org/swagger/index.html)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [GitHub Actions](https://github.com/features/actions)

## License

MIT License - Feel free to use and modify for your own bus-catching needs!
