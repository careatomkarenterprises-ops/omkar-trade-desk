import logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class TelegramReportEngine:
    """
    Clean production wrapper for Telegram sending
    """

    def __init__(self):
        self.poster = TelegramPoster()

    def send_message(self, channel: str, message: str) -> bool:
        try:
            return self.poster.send_message(channel, message)
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False
