import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        # ✅ FIX: Added 'education' to match your 3-channel setup
        self.channels = {
            "free": os.getenv("CHANNEL_FREE"),
            "premium": os.getenv("CHANNEL_PREMIUM"),
            "education": os.getenv("CHANNEL_EDUCATION"),
            "currency": os.getenv("CHANNEL_CURRENCY"),
            "commodity": os.getenv("CHANNEL_COMMODITY"),
        }

    def send_message(self, chat_type, message):
        try:
            chat_id = self.channels.get(chat_type)
            if not self.bot_token or not chat_id:
                logger.error(f"❌ Missing Telegram config for {chat_type}")
                return

            # ✅ FIX: Safety check to prevent "Empty Message" API errors
            if not message or len(str(message).strip()) == 0:
                logger.warning(f"⚠️ Attempted to send empty message to {chat_type}. Skipping.")
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
