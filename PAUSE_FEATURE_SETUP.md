# Pause/Resume Alerts Setup Guide

This feature allows you to send commands to your Telegram bot to pause alerts once you've boarded the bus.

## Commands

- `/stop` or `/boarded` - Pause all bus alerts
- `/start` - Resume bus alerts
- `/help` - Show help message

---

## Setup Steps

### 1. Create a GitHub Personal Access Token (PAT)

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: "Metro Transit Bot Commands"
4. Set expiration: **No expiration** (or your preference)
5. Select scopes:
   - ✅ **repo** (Full control of private repositories)
6. Click **"Generate token"**
7. **Copy the token** (you won't see it again!)

### 2. Add GitHub Repository Secret

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
2. Add a new secret:
   - **Name**: `PAT_TOKEN`
   - **Value**: Your personal access token from step 1

### 3. Enable Write Permissions for Workflows

1. Go to your repository → **Settings** → **Actions** → **General**
2. Scroll to **"Workflow permissions"**
3. Select **"Read and write permissions"**
4. Click **Save**

---

## Two Deployment Options

### Option A: Simple GitHub Actions Only (Recommended)

This uses GitHub Actions workflows only - no additional server needed.

**How it works:**
- You'll manually trigger the pause/resume via GitHub mobile app
- Simpler setup, no server needed
- Still very convenient via mobile app

**Steps:**
1. Install GitHub mobile app
2. When you board the bus:
   - Open GitHub app → Your repo → Actions
   - Run the **"Pause/Resume Alerts"** workflow
   - Select event type: `pause-alerts`
3. To resume:
   - Same steps, but select: `resume-alerts`

---

### Option B: Full Telegram Bot Integration (Advanced)

This allows sending `/stop` and `/start` directly in Telegram.

**Requires:**
- A server or free hosting (Railway, Fly.io, PythonAnywhere, etc.)
- Running the bot command handler continuously

**Steps:**

1. **Install dependencies on your server:**
   ```bash
   pip install python-telegram-bot requests
   ```

2. **Set environment variables:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export GITHUB_PAT="your_personal_access_token"
   export GITHUB_REPO="username/metro_transit_pings"
   ```

3. **Run the bot:**
   ```bash
   python telegram_bot_commands.py
   ```

4. **Keep it running:**
   - Use screen/tmux, systemd service, or process manager
   - Or deploy to a free hosting service

**Free Hosting Options:**
- **Railway.app** - Free tier, easy deployment
- **Fly.io** - Free tier, good for bots
- **PythonAnywhere** - Free tier for simple bots
- **Replit** - Free tier with always-on option

---

## How It Works

1. **You send `/boarded`** to your Telegram bot
2. **Bot triggers GitHub Actions** via repository dispatch webhook
3. **GitHub Actions creates** `.pause_state.json` file with `{"paused": true}`
4. **Main alert script checks** this file before sending alerts
5. **If paused**, it exits early without sending notifications

---

## Testing

### Test Pause Functionality

1. **Commit and push changes:**
   ```bash
   git add .
   git commit -m "Add pause/resume alerts feature"
   git push
   ```

2. **Trigger the pause workflow manually:**
   - Go to GitHub Actions
   - Click **"Pause/Resume Alerts"**
   - Click **"Run workflow"**
   - In the dropdown, select `pause-alerts`
   - Run it

3. **Check if it worked:**
   - The workflow should create `.pause_state.json` in your repo
   - Check the file contents: `{"paused": true, "paused_at": "..."}`

4. **Test the main workflow:**
   - Run the **"Bus Alert Workflow"** manually
   - It should exit early with message: "⏸️ Alerts are currently paused"

5. **Resume alerts:**
   - Run **"Pause/Resume Alerts"** with `resume-alerts`
   - The pause state should update to `{"paused": false}`

---

## Recommended Approach

For most users, **Option A (GitHub mobile app)** is the best balance:
- ✅ No server required
- ✅ Easy setup
- ✅ Reliable
- ✅ Works from your phone
- ⚠️ Requires 2-3 taps instead of a single command

If you really want the `/stop` command convenience, deploy **Option B** on a free hosting service.

---

## Troubleshooting

**Workflow says "Error: Process completed with exit code 1"**
- Check that write permissions are enabled
- Verify your PAT token has repo scope

**Bot doesn't respond to commands**
- Check the bot token is correct
- Verify GitHub PAT is set correctly
- Check the GITHUB_REPO format: `username/repo-name`

**Pause state doesn't persist**
- Ensure workflow has write permissions
- Check the git commit step succeeded in workflow logs

---

Good luck! 🚌