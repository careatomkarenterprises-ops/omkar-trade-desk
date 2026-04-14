"""
Telegram Poster - Omkar Elite Multi-Segment Version
Fixed with Active Debugging
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict

# Set up logging to show in GitHub Actions console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            print("❌ CRITICAL: TELEGRAM_BOT_TOKEN is missing from GitHub Secrets!")
            raise ValueError("TELEGRAM_BOT_TOKEN not set")

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        # ✅ Expanded Channels - Lowercase keys to match Agent calls
        self.channels = {
            'premium': os.getenv('CHANNEL_PREMIUM'),
            'education': os.getenv('CHANNEL_EDUCATION'),
            'fno': os.getenv('CHANNEL_FNO'),
            'nifty': os.getenv('CHANNEL_NIFTY'),
            'banknifty': os.getenv('CHANNEL_BANKNIFTY'),
            'swing': os.getenv('CHANNEL_SWING'),
            'currency': os.getenv('CHANNEL_CURRENCY'),
            'commodity': os.getenv('CHANNEL_COMMODITY')
        }

        # ✅ CLEAN LEGAL DISCLAIMER
        self.disclaimer = """
━━━━━━━━━━━━━━━━━━━━
📚 Omkar Market Intelligence

⚠️ AI-based market insights for educational purposes only.
❗ No investment advice or recommendations.
📊 Markets are subject to risk.
"""

    def send_message(self, channel: str, message: str) -> Dict:
        try:
            # Step 1: Check if channel mapping exists
            channel_key = channel.lower()
            chat_id = self.channels.get(channel_key)

            if not chat_id:
                error_msg = f"Mapping Failed: No Secret found for '{channel_key}'. Check GitHub Secrets!"
                print(f"⚠️ {error_msg}")
                return {'success': False, 'error': error_msg}

            # Step 2: Attempt to send
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message + self.disclaimer,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }

            print(f"📡 Attempting to post to {channel_key} (ID: {chat_id})...")
            response = requests.post(url, json=payload, timeout=15)

            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ SUCCESS: Message posted to {channel_key}!")
                    return {'success': True}
                else:
                    err = result.get('description')
                    print(f"❌ TELEGRAM REFUSED: {err}")
                    return {'success': False, 'error': err}
            else:
                print(f"❌ CONNECTION ERROR: HTTP {response.status_code} - {response.text}")
                return {'success': False, 'error': response.text}

        except Exception as e:
            print(f"💥 PYTHON CRASH: {str(e)}")
            return {'success': False, 'error': str(e)}

# ✅ THE "BRIDGE" FUNCTION
def send_to_telegram(segment: str, message: str):
    poster = TelegramPoster()
    return poster.send_message(segment, message)
