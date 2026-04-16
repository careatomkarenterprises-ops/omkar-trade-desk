import datetime
import logging

from src.scanner.premarket_prediction_engine import PreMarketPredictionEngine
from src.scanner.eod_engine import EODEngine
from src.scanner.learning_engine import LearningEngine
from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.telegram_report_engine import TelegramReportEngine

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector


# -------------------------------
# LOGGING SETUP
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================================================
# 🚀 MAIN ORCHESTRATION ENGINE (PRODUCTION VERSION)
# =========================================================
def main():

    now = datetime.datetime.now()

    logger.info("=" * 60)
    logger.info(f"🕒 MARKET INTELLIGENCE SYSTEM STARTED | {now}")
    logger.info("=" * 60)

    # -------------------------------
    # 🌍 GLOBAL MARKET ENGINE
    # -------------------------------
    global_engine = GlobalMarketEngine()
    global_data = global_engine.run()

    logger.info(f"🌍 GLOBAL BIAS: {global_data.get('overall_bias')}")

    # -------------------------------
    # CORE COMPONENTS INIT
    # -------------------------------
    fetcher = DataFetcher()
    detector = PatternDetector()
    telegram = TelegramReportEngine()

    # -------------------------------
    # SYMBOLS LIST (F&O)
    # -------------------------------
    try:
        symbols = fetcher.get_fno_symbols()
    except Exception:
        symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    logger.info(f"📊 TOTAL SYMBOLS LOADED: {len(symbols)}")

    # =========================================================
    # 🚀 PREMARKET ENGINE (BEFORE MARKET OPEN)
    # =========================================================
    if now.hour < 9:

        logger.info("🚀 PREMARKET MODE ACTIVATED")

        pre_engine = PreMarketPredictionEngine(
            data_fetcher=fetcher,
            pattern_detector=detector
        )

        top_setups = pre_engine.run(symbols, global_data)

        logger.info(f"🔥 TOP SETUPS GENERATED: {len(top_setups)}")

        # -------------------------------
        # 📩 TELEGRAM PREMARKET REPORT
        # -------------------------------
        telegram.send_premarket_report(global_data, top_setups)

    # =========================================================
    # 📊 LIVE MARKET MODE
    # =========================================================
    elif 9 <= now.hour < 16:

        logger.info("📊 LIVE MARKET MODE ACTIVE")

        logger.info("👉 Use core.py / GitHub workflow for real-time scanning")

    # =========================================================
    # 📉 EOD ENGINE
    # =========================================================
    else:

        logger.info("📉 EOD MODE ACTIVATED")

        eod_engine = EODEngine()
        eod_data = eod_engine.run(global_data)

        # -------------------------------
        # 📩 TELEGRAM EOD REPORT
        # -------------------------------
        telegram.send_eod_report(eod_data)

        # -------------------------------
        # 🧠 LEARNING ENGINE
        # -------------------------------
        logger.info("🧠 LEARNING ENGINE RUNNING")

        learner = LearningEngine()
        learner.run(global_data)

    logger.info("=" * 60)
    logger.info("✅ MARKET INTELLIGENCE CYCLE COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    main()
