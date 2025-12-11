# Setup Guide - Metro Transit Pings

## Quick Start Checklist

- [ ] 1. Verify Telegram bot is working
- [ ] 2. Test API connection
- [ ] 3. Configure GitHub Secrets
- [ ] 4. Push code to GitHub
- [ ] 5. Enable GitHub Actions
- [ ] 6. Test the workflow manually

---

## Step 1: Test Telegram Bot

Run the test script to verify your Telegram bot is working:

```bash
python3 test_telegram.py
```

When prompted, enter:
- Your bot token (from @BotFather)
- Your chat ID (from @userinfobot)

You should receive a test message on Telegram!

---

## Step 2: Test API Connection

Verify we can fetch bus data from Metro Transit:

```bash
python3 test_api.py
```

You should see upcoming departures for:
- Route 17 to Blake Road
- E Line to Southdale

---

## Step 3: Configure GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these two secrets:

### TELEGRAM_BOT_TOKEN
- **Name**: `TELEGRAM_BOT_TOKEN`
- **Value**: Your bot token from @BotFather (looks like `123456789:ABCdefGhIjKlmNoPQRsTUVwxyZ`)

### TELEGRAM_CHAT_ID
- **Name**: `TELEGRAM_CHAT_ID`
- **Value**: Your chat ID from @userinfobot (looks like `987654321`)

---

## Step 4: Push to GitHub

If you haven't already pushed the code:

```bash
git add .
git commit -m "Set up Metro Transit alert system"
git push origin main
```

---

## Step 5: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. If prompted, click **"I understand my workflows, go ahead and enable them"**

---

## Step 6: Test the Workflow

### Option A: Manual Trigger (Recommended for first test)

1. Go to **Actions** tab
2. Click **"Bus Alert System"** workflow
3. Click **"Run workflow"** button
4. Click the green **"Run workflow"** button
5. Wait a moment, then refresh - you should see a new workflow run
6. Click on the run to see the logs

### Option B: Wait for Scheduled Run

The workflow will automatically run:
- Every 5 minutes between 8:00 AM - 9:10 AM Central Time
- Monday through Friday only

---

## Troubleshooting

### API Test Shows No Departures

This is normal if:
- It's late at night (no buses running)
- It's outside normal service hours

Try again during daytime hours!

### Telegram Test Fails

Check that:
- Bot token is correct (no extra spaces)
- Chat ID is correct (no extra spaces)
- You've sent at least one message to your bot

### GitHub Actions Fails

1. Check the workflow run logs in the Actions tab
2. Verify secrets are set correctly
3. Look for error messages in the logs

---

## Configuration

Your current configuration:

- **Stop**: #50196 (Uptown Transit Station - Gate A)
- **Routes**:
  - Route 17 to Blake Road (Westbound)
  - E Line to Southdale (Southbound)
- **Schedule**: Weekdays, 8:00 AM - 9:10 AM
- **Walking time**: 3 minutes
- **Advance notice**: 15 minutes

To change these, edit [config.yaml](config.yaml)

---

## What Happens Next?

Once everything is set up:

1. **Every 5 minutes** (during your active window), GitHub Actions will:
   - Fetch real-time bus data
   - Check if any buses need alerts
   - Send you a Telegram message if it's time to leave

2. **You'll receive an alert** like:
   ```
   🚌 Time to head out!

   17 to Blake Road
   🚏 Departs: 8:45 AM (in 20 min)
   🚶 Leave by: 8:42 AM (in 17 min)
   ```

3. **If a bus is delayed**, you'll get an update:
   ```
   ⚠️ Bus Update - 17 Delayed

   Original: 8:45 AM
   Now: 8:52 AM (+7 min delay)

   🚶 New leave time: 8:49 AM (in 6 min)
   ```

---

## Need Help?

- Check the [README.md](README.md) for full documentation
- Look at workflow logs in the Actions tab
- Verify your configuration in [config.yaml](config.yaml)

Enjoy never missing your bus! 🚌
