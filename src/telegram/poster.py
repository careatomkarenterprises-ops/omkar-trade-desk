"""
Telegram Poster - Omkar Elite Multi-Segment Version
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        # ✅ Expanded Channels for Multi-Segment Scanner
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
            # Convert channel names to lowercase to prevent matching errors
            chat_id = self.channels.get(channel.lower())

            if not chat_id:
                logger.error(f"Channel ID not found for: {channel}")
                return {'success': False, 'error': f'Channel {channel} not found'}

            url = f"{self.base_url}/sendMessage"

            payload = {
                'chat_id': chat_id,
                'text': message + self.disclaimer,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }

            response = requests.post(url, json=payload, timeout=15)

            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return {'success': True}
                else:
                    return {'success': False, 'error': result.get('description')}
            else:
                return {'success': False, 'error': response.text}

        except Exception as e:
            logger.error(f"Telegram Error: {e}")
            return {'success': False, 'error': str(e)}

# ✅ THE "BRIDGE" FUNCTION
# This fixes the ImportError in your Agents
def send_to_telegram(segment: str, message: str):
    poster = TelegramPoster()
    return poster.send_message(segment, message)
