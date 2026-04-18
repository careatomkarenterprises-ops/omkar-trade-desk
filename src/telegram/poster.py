import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
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
                return False

            if not message or len(str(message).strip()) == 0:
                return False

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, data=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Message sent to {chat_type}")
                return True
            else:
                logger.error(f"❌ Telegram API Error for {chat_type}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Telegram Error: {e}")
            return False


# ✅ GLOBAL WRAPPER FOR ROUTER (DO NOT REMOVE)
def send_message(channel, message):
    """
    Wrapper function to use TelegramPoster inside router
    """
    try:
        poster = TelegramPoster()
        return poster.send_message(channel, message)
    except Exception as e:
        print(f"Telegram send error: {e}")
