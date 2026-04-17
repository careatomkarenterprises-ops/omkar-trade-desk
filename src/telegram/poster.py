import logging
import requests
import os

logger = logging.getLogger(__name__)


class TelegramPoster:

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.bot_token or not self.chat_id:
            logger.warning("⚠ Telegram credentials missing")

    def send_message(self, chat_type, message):

        try:
            if not self.bot_token or not self.chat_id:
                logger.error("❌ Cannot send message - Missing credentials")
                return

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            requests.post(url, data=payload)

            logger.info(f"✅ Message sent to {chat_type}")

        except Exception as e:
            logger.error(f"❌ Telegram Error: {e}")


# ✅ SUPPORT FUNCTION FOR AGENTS
def send_to_telegram(chat_type, message):
    try:
        TelegramPoster().send_message(chat_type, message)
    except Exception as e:
        logger.error(f"❌ send_to_telegram failed: {e}")
