import logging
import sys
import os

# Set up logging to show in GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_health_check():
    logger.info("🚀 STARTING SYSTEM HEALTH CHECK")
    
    try:
        # Step 1: Check if we can import our modules
        logger.info("📦 Importing modules...")
        from src.scanner.zerodha_fetcher import DataFetcher
        from src.scanner.patterns import PatternDetector
        from src.telegram.poster import TelegramPoster
        
        # Step 2: Test Zerodha Connection
        logger.info("🔌 Testing Zerodha Connection...")
        fetcher = DataFetcher()
        if fetcher.kite is None:
            logger.error("❌ Zerodha connection failed. Check your KITE_ACCESS_TOKEN.")
            return False
            
        # Step 3: Test Data Fetching
        logger.info("📊 Fetching test data (RELIANCE)...")
        data = fetcher.get_stock_data("RELIANCE")
        if data is None or data.empty:
            logger.error("❌ Could not fetch market data.")
            return False
        logger.info("✅ Market data received.")

        # Step 4: Test Telegram (Optional but helpful)
        logger.info("📲 Sending Telegram heartbeat...")
        try:
            poster = TelegramPoster()
            poster.send_message("🧪 Omkar Engine Health Check: PASS")
            logger.info("✅ Telegram message sent.")
        except Exception as te:
            logger.warning(f"⚠️ Telegram test skipped/failed: {te}")

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("✅ ALL SYSTEMS OPERATIONAL")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return True

    except Exception as e:
        logger.error(f"💥 CRITICAL SYSTEM ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_health_check()
    if not success:
        sys.exit(1) # Tell GitHub the job failed
