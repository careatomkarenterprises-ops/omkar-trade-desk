import os
import logging
import requests

logger = logging.getLogger(__name__)


class TelegramPoster:

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")

        self.channels = {
            "free": os.getenv("CHANNEL_FREE"),
            "premium": os.getenv("CHANNEL_PREMIUM"),
            "intraday": os.getenv("CHANNEL_INTRADAY"),
        }

    def send_message(self, channel_type, message):

        try:
            chat_id = self.channels.get(channel_type)

            if not chat_id:
                logger.error(f"❌ Channel not found: {channel_type}")
                return

            url = f"https://api.telegram.org/bot{self.token}/sendMessage"

            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }

            response = requests.post(url, json=payload)

            if response.status_code == 200:
                logger.info(f"✅ Sent to {channel_type}")
            else:
                logger.error(f"❌ Telegram error: {response.text}")

        except Exception as e:
            logger.error(f"Telegram send failed: {e}")


# ✅ IMPORTANT: FUNCTION EXPORT (THIS FIXES YOUR ERROR)
poster = TelegramPoster()


def send_message(channel, message):
    poster.send_message(channel, message)
