import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class TelegramPoster:

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        # ✅ FIX: Use YOUR existing secrets
        self.channels = {
            "free": os.getenv("CHANNEL_FREE"),
            "premium": os.getenv("CHANNEL_PREMIUM"),
            "currency": os.getenv("CHANNEL_CURRENCY"),
            "commodity": os.getenv("CHANNEL_COMMODITY"),
        }

        if not self.bot_token:
            logger.warning("⚠ Telegram BOT TOKEN missing")

    def send_message(self, chat_type, message):

        try:
            chat_id = self.channels.get(chat_type)

            if not self.bot_token or not chat_id:
                logger.error(f"❌ Missing Telegram config for {chat_type}")
                return

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = requests.post(url, data=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"✅ Message sent to {chat_type}")
            else:
                logger.error(f"❌ Telegram API Error: {response.text}")

        except Exception as e:
            logger.error(f"❌ Telegram Error: {e}")


def send_to_telegram(chat_type, message):
    try:
        TelegramPoster().send_message(chat_type, message)
    except Exception as e:
        logger.error(f"❌ send_to_telegram failed: {e}")
