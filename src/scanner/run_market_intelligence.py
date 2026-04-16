import datetime
import logging

from src.scanner.premarket_prediction_engine import PreMarketPredictionEngine
from src.scanner.eod_engine import EODEngine
from src.scanner.learning_engine import LearningEngine
from src.scanner.global_market_engine import GlobalMarketEngine

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():

    now = datetime.datetime.now()

    logger.info(f"🕒 System Time: {now}")

    # -------------------------------
    # GLOBAL MARKET CONTEXT FIRST
    # -------------------------------
    global_engine = GlobalMarketEngine()
    global_data = global_engine.run()

    logger.info(f"🌍 Global Bias: {global_data.get('overall_bias')}")

    # -------------------------------
    # INIT CORE COMPONENTS
    # -------------------------------
    fetcher = DataFetcher()
    detector = PatternDetector()

    symbols = fetcher.get_fno_symbols() if hasattr(fetcher, "get_fno_symbols") else [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"
    ]

    # -------------------------------
    # 🚀 PREMARKET ENGINE (UPGRADED)
    # -------------------------------
    if now.hour < 9:

        logger.info("🚀 Running PREMARKET PREDICTION ENGINE")

        pre_engine = PreMarketPredictionEngine(
            data_fetcher=fetcher,
            pattern_detector=detector
        )

        top_setups = pre_engine.run(symbols, global_data)

        logger.info(f"🔥 Top Setups Found: {len(top_setups)}")

    # -------------------------------
    # 📊 MARKET HOURS
    # -------------------------------
    elif 9 <= now.hour < 16:

        logger.info("📊 Market Live Mode")

        logger.info("Scanner should run via core.py or GitHub workflow")

    # -------------------------------
    # 📉 EOD ENGINE
    # -------------------------------
    else:

        logger.info("📉 Running EOD ENGINE")

        eod = EODEngine()
        eod.run(global_data)

        logger.info("🧠 Running LEARNING ENGINE")

        learn = LearningEngine()
        learn.run(global_data)

    logger.info("✅ Market Intelligence Cycle Completed")


if __name__ == "__main__":
    main()
