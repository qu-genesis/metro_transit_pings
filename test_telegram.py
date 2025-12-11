#!/usr/bin/env python3
"""
Test script to verify Telegram bot is working.
"""

import os
import sys

# Prompt for credentials if not set as env vars
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if not bot_token:
    bot_token = input("Enter your Telegram bot token: ").strip()

if not chat_id:
    chat_id = input("Enter your Telegram chat ID: ").strip()

# Set environment variables for the notifier
os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
os.environ['TELEGRAM_CHAT_ID'] = chat_id

# Import after setting environment variables
from src.notifier import TelegramNotifier

print("=" * 60)
print("Telegram Bot Test")
print("=" * 60)
print()

try:
    notifier = TelegramNotifier()
    print("Sending test message...")

    success = notifier.send_test_message()

    if success:
        print("✓ Test message sent successfully!")
        print("Check your Telegram to confirm you received it.")
    else:
        print("✗ Failed to send test message")
        sys.exit(1)

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("Test complete!")
print("=" * 60)
