import logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class CommodityAgent:

    def __init__(self):
        self.telegram = TelegramPoster()

    def run(self):

        try:
            logger.info("🛢 Commodity Engine Running")

            # Dummy (replace later with real data)
            message = (
                "🛢 Commodity Update\n"
                "Gold: Bullish\n"
                "Crude: Sideways\n"
            )

            self.telegram.send_message("free", message)

        except Exception as e:
            logger.error("❌ Commodity Agent Failed")
            logger.exception(e)
