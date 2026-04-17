import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class TelegramPoster:

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # ✅ CHANNEL MAP (IMPORTANT)
        self.channels = {
            "free": self.chat_id,
            "premium": os.getenv("CHANNEL_PREMIUM", self.chat_id),
            "currency": self.chat_id,
            "commodity": self.chat_id
        }

        if not self.bot_token or not self.chat_id:
            logger.warning("⚠ Telegram credentials missing")

    def send_message(self, chat_type, message):

        try:
            target_id = self.channels.get(chat_type, self.chat_id)

            if not self.bot_token or not target_id:
                logger.error("❌ Cannot send message - Missing credentials")
                return

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            payload = {
                "chat_id": target_id,
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


# ✅ SUPPORT FUNCTION FOR AGENTS
def send_to_telegram(chat_type, message):
    try:
        TelegramPoster().send_message(chat_type, message)
    except Exception as e:
        logger.error(f"❌ send_to_telegram failed: {e}")
