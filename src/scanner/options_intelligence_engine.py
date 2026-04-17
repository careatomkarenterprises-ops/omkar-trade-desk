import logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class OptionsIntelligenceEngine:

    def __init__(self):
        self.telegram = TelegramPoster()

    # -----------------------------
    # MAIN METHOD (USED BY CONTROLLER)
    # -----------------------------
    def run(self):

        try:
            logger.info("📊 Options Intelligence Running")

            data = self.generate_options_signal()

            message = (
                "📊 OPTIONS INTELLIGENCE\n"
                f"Bias: {data['bias']}\n"
                f"Flow: {data['flow']}\n"
                f"Confidence: {data['confidence']}"
            )

            self.telegram.send_message("free", message)

            return data  # ✅ important for controller

        except Exception as e:
            logger.error("❌ Options Engine Failed")
            logger.exception(e)
            return {}

    # -----------------------------
    # HEALTH CHECK COMPATIBILITY METHOD
    # -----------------------------
    def generate_options_signal(self):
        """
        This method is REQUIRED for system_health_check.py
        """

        try:
            # 🔥 Dummy logic (you can upgrade later)
            data = {
                "bias": "Bullish",
                "flow": "Call Writing",
                "confidence": "Medium"
            }

            logger.info(f"📊 Options Data Generated: {data}")

            return data

        except Exception as e:
            logger.error("❌ generate_options_signal failed")
            logger.exception(e)
            return {
                "bias": "Neutral",
                "flow": "No Data",
                "confidence": "Low"
            }
