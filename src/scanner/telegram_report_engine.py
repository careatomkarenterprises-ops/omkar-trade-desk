import logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class TelegramReportEngine:
    """
    Simple wrapper around TelegramPoster
    Used by execution layer and system controller
    """

    def __init__(self):
        self.poster = TelegramPoster()

    def send_message(self, channel: str, message: str):
        try:
            return self.poster.send_message(channel, message)
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return Falseimport logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class TelegramReportEngine:
    """
    Simple wrapper around TelegramPoster
    Used by execution layer and system controller
    """

    def __init__(self):
        self.poster = TelegramPoster()

    def send_message(self, channel: str, message: str):
        try:
            return self.poster.send_message(channel, message)
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False
