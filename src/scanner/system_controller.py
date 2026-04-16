import datetime
import logging

from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.premarket_engine import PreMarketEngine
from src.scanner.eod_engine import EODEngine
from src.scanner.learning_engine import LearningEngine
from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemController:

    def __init__(self):
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.global_engine = GlobalMarketEngine()

    def run(self):

        now = datetime.datetime.now()

        logger.info(f"🚀 SYSTEM START | TIME: {now}")

        # STEP 1: GLOBAL CONTEXT
        global_data = self.global_engine.run()

        logger.info(f"🌍 GLOBAL BIAS: {global_data.get('overall_bias')}")

        symbols = self.fetcher.get_fno_symbols()

        if not symbols:
            logger.warning("No symbols found")
            return

        # STEP 2: PREMARKET
        if now.hour < 9:

            logger.info("🔥 PREMARKET ENGINE START")

            engine = PreMarketEngine()
            engine.run(symbols, global_data)

        # STEP 3: MARKET HOURS (light mode)
        elif 9 <= now.hour < 16:

            logger.info("📊 MARKET LIVE MODE - SCANNER ONLY")

            for symbol in symbols[:20]:  # limit load for GitHub stability

                try:
                    data = self.fetcher.get_stock_data(symbol)

                    if data is None or data.empty:
                        continue

                    result = self.detector.analyze(symbol, data)

                    if result and result.get("has_pattern"):
                        logger.info(f"🔥 SIGNAL: {symbol}")

                except Exception as e:
                    logger.error(f"{symbol} error: {e}")

        # STEP 4: EOD
        else:

            logger.info("📉 EOD ENGINE START")

            eod = EODEngine()
            eod.run(global_data)

            logger.info("🧠 LEARNING ENGINE START")

            learn = LearningEngine()
            learn.run(global_data)

        logger.info("✅ SYSTEM COMPLETE")


if __name__ == "__main__":
    SystemController().run()
