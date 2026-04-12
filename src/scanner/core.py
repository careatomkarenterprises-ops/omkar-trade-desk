import os
import logging
import pandas as pd
import time
from datetime import datetime

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OmkarTradeDesk:
    def __init__(self):
        logger.info("Initializing Omkar Trade Desk Core...")
        
        # Initialize DataFetcher (This handles the Auto-Login)
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.poster = TelegramPoster()
        
        self.symbols_file = 'fno_stocks.csv'

    def get_fno_symbols(self):
        """Load symbols from the CSV file"""
        try:
            if os.path.exists(self.symbols_file):
                df = pd.read_csv(self.symbols_file)
                return df['symbol'].tolist()
            else:
                logger.error(f"Symbols file {self.symbols_file} not found!")
                return ["RELIANCE", "TCS", "HDFCBANK", "INFY"]
        except Exception as e:
            logger.error(f"Error loading symbols: {e}")
            return []

    def execute_scan(self):
        """Main scanner loop for Institutional Volume Price Box detection"""
        
        # Check if login was successful
        if not self.fetcher.is_ready():
            error_msg = (
                "⚠️ **System Alert: Technical Issue**\n\n"
                "The live market data feed is currently experiencing a connection issue. "
                "The automated login sequence failed. Check TOTP Secret.\n\n"
                "🛠️ Restore connection manual check required."
            )
            logger.critical("Zerodha API not ready. Sending technical alert.")
            self.poster.send_message(channel='premium', message=error_msg)
            return 

        logger.info("🚀 Starting Market Scan...")
        symbols = self.get_fno_symbols()
        matches_found = 0

        for symbol in symbols:
            try:
                data = self.fetcher.get_stock_data(symbol) 
                
                if data is not None and not data.empty:
                    result = self.detector.analyze(symbol, data)
                    
                    if result and result.get('has_pattern'):
                        logger.info(f"✅ Pattern Found: {symbol}")
                        
                        message = (
                            f"🔍 **{result['trigger']}**\n\n"
                            f"🎫 **Symbol:** #{symbol}\n"
                            f"💰 **Price:** ₹{result['price']}\n"
                            f"📊 **Volume Surge:** {result['surge_ratio']}x\n"
                            f"📦 **Box Range:** {result['support']} - {result['resistance']}\n"
                            f"⚡ **Strength:** {'⭐' * int(result['strength'] * 5)}"
                        )
                        
                        self.poster.send_message(channel='premium', message=message)
                        matches_found += 1
                
                # Small delay to be gentle on the API
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue

        logger.info(f"🏁 Scan Complete. Found {matches_found} setups.")

def main():
    try:
        scanner = OmkarTradeDesk()
        scanner.execute_scan()
    except Exception as e:
        logger.critical(f"Critical System Failure: {e}")

if __name__ == "__main__":
    main()
