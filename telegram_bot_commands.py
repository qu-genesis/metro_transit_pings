#!/usr/bin/env python3
"""
Telegram Bot Command Handler
Listens for commands like /stop and /start to control alerts via GitHub API.

Run this on a server or use a webhook service.
"""

import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_PAT')  # Your Personal Access Token
GITHUB_REPO = os.getenv('GITHUB_REPO')  # Format: "username/repo-name"

# GitHub API endpoint for repository dispatch
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"


def trigger_github_action(action_type: str):
    """
    Trigger a GitHub Actions workflow via repository dispatch.

    Args:
        action_type: Either 'pause-alerts' or 'resume-alerts'
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    payload = {
        "event_type": action_type
    }

    try:
        response = requests.post(GITHUB_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error triggering GitHub Action: {e}")
        return False


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop or /boarded command."""
    await update.message.reply_text("⏸️ Pausing bus alerts...")

    if trigger_github_action('pause-alerts'):
        await update.message.reply_text(
            "✅ Bus alerts paused!\n\n"
            "You won't receive any more alerts until you send /start"
        )
    else:
        await update.message.reply_text("❌ Failed to pause alerts. Please try again.")


async def boarded_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /boarded command (same as /stop)."""
    await stop_command(update, context)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command to resume alerts."""
    await update.message.reply_text("▶️ Resuming bus alerts...")

    if trigger_github_action('resume-alerts'):
        await update.message.reply_text(
            "✅ Bus alerts resumed!\n\n"
            "You'll receive alerts again during your scheduled window."
        )
    else:
        await update.message.reply_text("❌ Failed to resume alerts. Please try again.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
🚌 *Bus Alert Bot Commands*

/stop - Pause all bus alerts
/boarded - Same as /stop (use when you've boarded)
/start - Resume bus alerts
/help - Show this help message

Once you send /stop or /boarded, you won't receive any more alerts until you send /start again.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


def main():
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_PAT environment variable not set")
    if not GITHUB_REPO:
        raise ValueError("GITHUB_REPO environment variable not set (format: username/repo-name)")

    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("boarded", boarded_command))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    print("Bot started! Send /stop or /boarded to pause alerts.")
    application.run_polling()


if __name__ == '__main__':
    main()
