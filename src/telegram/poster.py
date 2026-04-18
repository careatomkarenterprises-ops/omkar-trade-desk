import os
import logging
import requests

logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        # Map logical names to channel usernames (set these in GitHub Secrets)
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
                logger.info(f"Sent to {channel_type}")
            else:
                logger.error(f"Telegram error: {response.text}")
        except Exception as e:
            logger.error(f"Send failed: {e}")

_poster = TelegramPoster()

def send_message(channel_type, message):
    _poster.send_message(channel_type, message)

# Legacy function for any old code that expects send_alert
def send_alert(message, channel):
    for ctype, cid in _poster.channels.items():
        if cid == channel:
            _poster.send_message(ctype, message)
            return
    # Fallback: try sending directly
    try:
        url = f"https://api.telegram.org/bot{_poster.token}/sendMessage"
        requests.post(url, json={"chat_id": channel, "text": message, "parse_mode": "Markdown"})
    except:
        pass
