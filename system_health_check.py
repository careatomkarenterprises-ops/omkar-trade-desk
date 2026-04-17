import logging
import sys

# ✅ Import from our new corrected files
from src.scanner.zerodha_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
from src.telegram.poster import TelegramPoster

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ----------------------------
# 1. DATA FETCHER TEST
# ----------------------------
def test_data_fetcher():
    logger.info("🔍 Testing Data Fetcher (Zerodha)...")
    try:
        fetcher = DataFetcher()
        if not fetcher.kite:
            logger.error("❌ DataFetcher: Kite connection failed (Check Credentials)")
            return False
            
        # Try fetching a real stock to verify
        data = fetcher.get_stock_data("RELIANCE")
        if data is None or data.empty:
            logger.error("❌ DataFetcher: No market data received")
            return False

        logger.info(f"✅ DataFetcher OK | Rows: {len(data)}")
        return True
    except Exception as e:
        logger.error(f"❌ DataFetcher Error: {e}")
        return False

# ----------------------------
# 2. PATTERN ENGINE TEST
# ----------------------------
def test_pattern_engine():
    logger.info("🔍 Testing Pattern Engine...")
    try:
        fetcher = DataFetcher()
        detector = PatternDetector()
        
        data = fetcher.get_stock_data("RELIANCE")
        if data is None or data.empty:
            return False

        result = detector.analyze("RELIANCE", data)
        logger.info(f"📊 Pattern Analysis Result: {result}")
        return True
    except Exception as e:
        logger.error(f"❌ Pattern Engine Error: {e}")
        return False

# ----------------------------
# 3. GLOBAL ENGINE TEST
# ----------------------------
def test_global_engine():
    logger.info("🔍 Testing Global Market Engine...")
    try:
        engine = GlobalMarketEngine()
        data = engine.run()
        logger.info(f"🌍 Global Bias: {data.get('overall_bias')}")
        return data is not None
    except Exception as e:
        logger.error(f"❌ Global Engine Error: {e}")
        return False

# ----------------------------
# 4. OPTIONS ENGINE TEST
# ----------------------------
def test_options_engine():
    logger.info("🔍 Testing Options Engine...")
    try:
        engine = OptionsIntelligenceEngine()
        # We run the standard logic
        engine.run()
        logger.info("✅ Options Engine OK")
        return True
    except Exception as e:
        logger.error(f"❌ Options Engine Error: {e}")
        return False

# ----------------------------
# 5. TELEGRAM TEST
# ----------------------------
def test_telegram():
    logger.info("🔍 Testing Telegram Connection...")
    try:
        bot = TelegramPoster()
        bot.send_message("🧪 OMKAR SYSTEM HEALTH CHECK: Everything is Operational.")
        logger.info("✅ Telegram OK")
        return True
    except Exception as e:
        logger.error(f"❌ Telegram failed: {e}")
        return False

# ----------------------------
# MAIN TEST RUNNER
# ----------------------------
def main():
    logger.info("🚀 STARTING FULL SYSTEM HEALTH CHECK")
    
    results = {
        "Data Fetcher (Kite)": test_data_fetcher(),
        "Pattern Detector": test_pattern_engine(),
        "Global Markets": test_global_engine(),
        "Options Intelligence": test_options_engine(),
        "Telegram Poster": test_telegram()
    }

    logger.info("━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("📊 FINAL SYSTEM SUMMARY")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━")

    all_pass = True
    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{component}: {status}")
        if not success:
            all_pass = False

    if all_pass:
        logger.info("🚀 SYSTEM IS FULLY HEALTHY & READY FOR TRADING")
    else:
        logger.warning("⚠ SYSTEM HAS ISSUES - PLEASE CHECK LOGS ABOVE")
        sys.exit(1) # Tell GitHub the run failed if we have issues

if __name__ == "__main__":
    main()
