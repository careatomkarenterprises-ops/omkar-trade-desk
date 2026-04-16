import datetime
import logging

from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.premarket_engine import PreMarketPredictionEngine
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

        # -------------------------------
        # STEP 1: GLOBAL CONTEXT
        # -------------------------------
        global_data = self.global_engine.run()
        logger.info(f"🌍 GLOBAL BIAS: {global_data.get('overall_bias')}")

        symbols = self.fetcher.get_fno_symbols()

        if not symbols:
            logger.warning("⚠ No symbols found")
            return

        # -------------------------------
        # STEP 2: PREMARKET ENGINE
        # -------------------------------
        if now.hour < 9:

            logger.info("🔥 PREMARKET ENGINE START")

            try:
                engine = PreMarketPredictionEngine(
                    data_fetcher=self.fetcher,
                    pattern_detector=self.detector
                )

                result = engine.run(symbols, global_data)

                logger.info(f"📊 PREMARKET COMPLETED | SETUPS: {len(result) if result else 0}")

            except Exception as e:
                logger.error(f"❌ PreMarket Engine Error: {e}")

        # -------------------------------
        # STEP 3: MARKET LIVE MODE
        # -------------------------------
        elif 9 <= now.hour < 16:

            logger.info("📊 MARKET LIVE MODE - SCANNER ONLY")

            for symbol in symbols[:20]:

                try:
                    data = self.fetcher.get_stock_data(symbol)

                    if data is None or data.empty:
                        continue

                    result = self.detector.analyze(symbol, data)

                    if result and result.get("has_pattern"):
                        logger.info(f"🔥 SIGNAL DETECTED: {symbol}")

                except Exception as e:
                    logger.error(f"❌ {symbol} error: {e}")

        # -------------------------------
        # STEP 4: EOD ENGINE
        # -------------------------------
        else:

            logger.info("📉 EOD ENGINE START")

            try:
                eod = EODEngine()
                eod.run(global_data)
            except Exception as e:
                logger.error(f"❌ EOD Error: {e}")

            logger.info("🧠 LEARNING ENGINE START")

            try:
                learn = LearningEngine()
                learn.run(global_data)
            except Exception as e:
                logger.error(f"❌ Learning Error: {e}")

        logger.info("✅ SYSTEM COMPLETE SUCCESSFULLY")


if __name__ == "__main__":
    SystemController().run()
