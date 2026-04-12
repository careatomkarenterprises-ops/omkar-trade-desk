import os
import logging
import pandas as pd
from datetime import datetime

# Import your custom modules
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
        
        # Initialize sub-modules
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.poster = TelegramPoster()
        
        # Path to your F&O symbols list
        self.symbols_file = 'fno_stocks.csv'

    def get_fno_symbols(self):
        """Load symbols from the CSV file"""
        try:
            if os.path.exists(self.symbols_file):
                df = pd.read_csv(self.symbols_file)
                return df['symbol'].tolist()
            else:
                logger.error(f"Symbols file {self.symbols_file} not found!")
                # Fallback to a small list if file is missing
                return ["RELIANCE", "TCS", "HDFCBANK", "INFY"]
        except Exception as e:
            logger.error(f"Error loading symbols: {e}")
            return []

    def execute_scan(self):
        """
        Main scanner loop for Institutional Volume Price Box detection
        """
        logger.info("🚀 Starting Market Scan...")
        symbols = self.get_fno_symbols()
        matches_found = 0

        for symbol in symbols:
            try:
                # 1. Fetch data (Uses Zerodha with Yahoo fallback)
                # Requesting enough days to calculate 15 SMA + 6 day quiet period
                data = self.fetcher.get_stock_data(symbol) 
                
                if data is not None and not data.empty:
                    # 2. Run the refined Pattern Detector
                    result = self.detector.analyze(symbol, data)
                    
                    # 3. If institutional footprint is detected, post to Telegram
                    if result and result.get('has_pattern'):
                        logger.info(f"✅ Pattern Found: {symbol} - {result['trigger']}")
                        
                        # Create a clean message for Telegram
                        message = (
                            f"🔍 **{result['trigger']}**\n\n"
                            f"🎫 **Symbol:** #{symbol}\n"
                            f"💰 **Price:** ₹{result['price']}\n"
                            f"📊 **Volume Surge:** {result['surge_ratio']}x\n"
                            f"📦 **Box Range:** {result['support']} - {result['resistance']}\n"
                            f"⚡ **Strength:** {'⭐' * int(result['strength'] * 5)}"
                        )
                        
                        # Post specifically to the F&O channel
                        self.poster.send_message(channel='premium', message=message)
                        matches_found += 1
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue

        logger.info(f"🏁 Scan Complete. Found {matches_found} setups.")

def main():
    """Entry point for GitHub Actions"""
    try:
        scanner = OmkarTradeDesk()
        scanner.execute_scan()
    except Exception as e:
        logger.critical(f"Critical System Failure: {e}")

if __name__ == "__main__":
    main()
