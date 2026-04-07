"""
Telegram Poster - Clean & Fixed Version
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

        # Channels
        self.channels = {
            'premium': os.getenv('CHANNEL_PREMIUM'),
            'education': os.getenv('CHANNEL_EDUCATION')
        }

        # ✅ CLEAN LEGAL DISCLAIMER (FIXED INDENTATION)
        self.disclaimer = """
━━━━━━━━━━━━━━━━━━━━
📚 Omkar Market Intelligence

⚠️ AI-based market insights for educational purposes only.
❗ No investment advice or recommendations.
📊 Markets are subject to risk.
"""

    def send_message(self, channel: str, message: str) -> Dict:

        try:
            chat_id = self.channels.get(channel)

            if not chat_id:
                return {'success': False, 'error': 'Channel not found'}

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
