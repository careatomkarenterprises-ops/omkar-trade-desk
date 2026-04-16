import logging

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
from src.telegram.telegram_report_engine import TelegramReportEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_data_fetcher():
    logger.info("🔍 Testing Data Fetcher...")

    fetcher = DataFetcher()

    if not fetcher.is_ready():
        logger.error("❌ DataFetcher NOT READY")
        return False

    data = fetcher.get_stock_data("RELIANCE")

    if data is None or data.empty:
        logger.error("❌ No market data received")
        return False

    logger.info(f"✅ DataFetcher OK | Rows: {len(data)}")
    return True


def test_pattern_engine():
    logger.info("🔍 Testing Pattern Engine...")

    fetcher = DataFetcher()
    detector = PatternDetector()

    data = fetcher.get_stock_data("RELIANCE")

    result = detector.analyze("RELIANCE", data)

    logger.info(f"📊 Pattern Result: {result}")

    return result is not None


def test_global_engine():
    logger.info("🔍 Testing Global Market Engine...")

    engine = GlobalMarketEngine()
    data = engine.run()

    logger.info(f"🌍 Global Data: {data}")

    return data is not None


def test_options_engine():
    logger.info("🔍 Testing Options Engine...")

    fetcher = DataFetcher()

    nifty = fetcher.get_stock_data("NIFTY 50")
    banknifty = fetcher.get_stock_data("BANKNIFTY")

    engine = OptionsIntelligenceEngine()

    signal = engine.generate_options_signal(nifty, banknifty)

    logger.info(f"📊 Options Signal: {signal}")

    return signal is not None


def test_telegram():
    logger.info("🔍 Testing Telegram (SAFE MODE)...")

    try:
        bot = TelegramReportEngine()
        bot.send_message("free", "🧪 SYSTEM TEST SUCCESS - OMKAR ENGINE ACTIVE")
        logger.info("✅ Telegram OK")
        return True
    except Exception as e:
        logger.error(f"❌ Telegram failed: {e}")
        return False


def main():

    logger.info("🚀 STARTING FULL SYSTEM HEALTH CHECK")

    results = {
        "data_fetcher": test_data_fetcher(),
        "pattern_engine": test_pattern_engine(),
        "global_engine": test_global_engine(),
        "options_engine": test_options_engine(),
        "telegram": test_telegram()
    }

    logger.info("━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("📊 SYSTEM TEST SUMMARY")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━")

    for k, v in results.items():
        status = "✅ PASS" if v else "❌ FAIL"
        logger.info(f"{k}: {status}")

    if all(results.values()):
        logger.info("🚀 SYSTEM IS FULLY HEALTHY")
    else:
        logger.warning("⚠ SYSTEM HAS ISSUES - FIX REQUIRED")


if __name__ == "__main__":
    main()
