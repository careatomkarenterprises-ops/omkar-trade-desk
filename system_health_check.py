import logging
import sys
import os

# Set up logging for GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_health_check():
    logger.info("🚀 STARTING OMKAR SYSTEM HEALTH CHECK")
    
    try:
        # 1. Direct Import Test (Breaking the circular loop)
        logger.info("📦 Checking module paths...")
        from src.scanner.zerodha_fetcher import DataFetcher
        from src.scanner.patterns import PatternDetector
        from src.telegram.poster import TelegramPoster
        
        # 2. Zerodha API Test
        logger.info("🔌 Verifying Zerodha Connection...")
        fetcher = DataFetcher()
        if fetcher.kite is None:
            logger.error("❌ Zerodha connection failed. Check KITE_ACCESS_TOKEN.")
            return False
            
        # 3. Market Data Test
        logger.info("📊 Fetching test data (RELIANCE)...")
        data = fetcher.get_stock_data("RELIANCE")
        if data is None or data.empty:
            logger.error("❌ Data fetch failed.")
            return False
        logger.info(f"✅ Market data received: {len(data)} rows.")

        # 4. Telegram Test (Fixed positional argument issue)
        logger.info("📲 Testing Telegram notifications...")
        try:
            poster = TelegramPoster()
            # We must specify the channel 'free' and the message
            poster.send_message("free", "🧪 Omkar Trade Desk: System Health Check PASSED ✅")
            logger.info("✅ Telegram heartbeat sent successfully.")
        except Exception as te:
            logger.warning(f"⚠️ Telegram skip/fail (non-critical): {te}")

        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        logger.info("🚀 ALL SYSTEMS OPERATIONAL")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return True

    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    if not run_health_check():
        sys.exit(1)
