import os
import logging
import requests

logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        # Use the secrets you already have (CHANNEL_FREE and CHANNEL_PREMIUM)
        # Map logical channel types to your existing secrets
        self.channels = {
            "free_main": os.getenv("CHANNEL_FREE", "@OmkarTradeDesk"),
            "free_signals": os.getenv("CHANNEL_FREE", "@OmkarTradeDesk"),  # same free channel
            "premium": os.getenv("CHANNEL_PREMIUM", "@OmkarIntraday"),
            "premium_elite": os.getenv("CHANNEL_PREMIUM", "@OmkarIntraday"),  # same premium channel
        }

    def send_message(self, channel_type, message):
        try:
            chat_id = self.channels.get(channel_type)
            if not chat_id:
                logger.error(f"Channel {channel_type} not configured")
                return
            
            # Ensure chat_id has @ prefix
            if not chat_id.startswith('@'):
                chat_id = f"@{chat_id}"
            
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Sent to {channel_type} ({chat_id})")
            else:
                error_text = response.text
                logger.error(f"❌ Telegram error for {chat_id}: {error_text}")
                if "chat not found" in error_text:
                    logger.error(f"   → Make sure your bot is an admin in {chat_id}")
                    logger.error(f"   → And that the channel username is correct")
        except Exception as e:
            logger.error(f"Send failed: {e}")

_poster = TelegramPoster()

def send_message(channel_type, message):
    _poster.send_message(channel_type, message)

def send_alert(message, channel_username):
    """Legacy function for compatibility"""
    for ctype, cid in _poster.channels.items():
        if cid == channel_username:
            _poster.send_message(ctype, message)
            return
    try:
        url = f"https://api.telegram.org/bot{_poster.token}/sendMessage"
        requests.post(url, json={"chat_id": channel_username, "text": message, "parse_mode": "Markdown"})
    except:
        logger.error(f"Failed to send to {channel_username}")