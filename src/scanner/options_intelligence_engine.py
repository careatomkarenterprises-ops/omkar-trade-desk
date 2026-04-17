import logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class OptionsIntelligenceEngine:

    def __init__(self):
        self.telegram = TelegramPoster()

    def run(self):

        try:
            logger.info("📊 Options Intelligence Running")

            data = {
                "bias": "Bullish",
                "flow": "Call Writing",
                "confidence": "Medium"
            }

            message = (
                "📊 OPTIONS INTELLIGENCE\n"
                f"Bias: {data['bias']}\n"
                f"Flow: {data['flow']}\n"
                f"Confidence: {data['confidence']}"
            )

            self.telegram.send_message("free", message)

            return data  # ✅ IMPORTANT FIX

        except Exception as e:
            logger.error("❌ Options Engine Failed")
            logger.exception(e)
            return {}
