import os
import logging
import requests

logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        # ONLY 4 channels – read from environment
        self.channels = {
            "free_main": os.getenv("CHANNEL_FREE_MAIN", "@OmkarFree"),
            "free_signals": os.getenv("CHANNEL_FREE_SIGNALS", "@OmkarFreeSignals"),
            "premium": os.getenv("CHANNEL_PREMIUM", "@OmkarPro"),
            "premium_elite": os.getenv("CHANNEL_PREMIUM_ELITE", "@OmkarProElite"),
        }

    def send_message(self, channel_type, message):
        try:
            chat_id = self.channels.get(channel_type)
            if not chat_id:
                logger.error(f"Channel {channel_type} not configured")
                return
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Sent to {channel_type} ({chat_id})")
            else:
                logger.error(f"Telegram error: {response.text}")
        except Exception as e:
            logger.error(f"Send failed: {e}")

_poster = TelegramPoster()

def send_message(channel_type, message):
    _poster.send_message(channel_type, message)

# Legacy support for old code that uses send_alert(channel_username, message)
def send_alert(message, channel_username):
    for ctype, cid in _poster.channels.items():
        if cid == channel_username:
            _poster.send_message(ctype, message)
            return
    # Fallback: try direct send
    try:
        url = f"https://api.telegram.org/bot{_poster.token}/sendMessage"
        requests.post(url, json={"chat_id": channel_username, "text": message, "parse_mode": "Markdown"})
    except:
        logger.error(f"Failed to send to {channel_username}")
