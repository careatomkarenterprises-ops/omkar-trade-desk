import logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class OptionsIntelligenceEngine:

    def __init__(self):
        self.telegram = TelegramPoster()

    def run(self):

        try:
            logger.info("📊 Options Intelligence Running")

            message = (
                "📊 OPTIONS INTELLIGENCE\n"
                "Bias: Bullish\n"
                "Flow: Call Writing\n"
                "Confidence: Medium"
            )

            self.telegram.send_message("free", message)

        except Exception as e:
            logger.error("❌ Options Engine Failed")
            logger.exception(e)
