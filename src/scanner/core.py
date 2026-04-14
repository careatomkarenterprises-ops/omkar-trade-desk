import os
import logging
import pandas as pd
import time
import json
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
        
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.poster = TelegramPoster()
        
        self.symbols_file = 'fno_stocks.csv'
        self.history_file = 'data/sent_alerts.json'
        os.makedirs('data', exist_ok=True)
        
        # Load memory of sent alerts
        self.sent_alerts = self._load_history()

    def _load_history(self):
        """Load the list of stocks already alerted today"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    # Only keep history if it's from today
                    if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                        return data.get('symbols', [])
            except Exception as e:
                logger.error(f"Error loading history: {e}")
        return []

    def _save_history(self, symbol):
        """Add a stock to today's 'already sent' list"""
        self.sent_alerts.append(symbol)
        try:
            with open(self.history_file, 'w') as f:
                json.dump({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'symbols': self.sent_alerts
                }, f)
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def get_fno_symbols(self):
        try:
            if os.path.exists(self.symbols_file):
                df = pd.read_csv(self.symbols_file)
                return df['symbol'].tolist()
            return ["RELIANCE", "TCS", "HDFCBANK", "INFY"]
        except Exception as e:
            logger.error(f"Error loading symbols: {e}")
            return []

    def execute_scan(self):
        if not self.fetcher.is_ready():
            error_msg = "⚠️ **System Alert: Connection Issue**\nCheck Zerodha Login."
            self.poster.send_message(channel='premium', message=error_msg)
            return 

        logger.info("🚀 Starting Market Scan...")
        symbols = self.get_fno_symbols()
        matches_found = 0

        for symbol in symbols:
            # SKIP if we already alerted this stock today
            if symbol in self.sent_alerts:
                logger.info(f"⏭️ Skipping {symbol} (Already alerted today)")
                continue

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
                        self._save_history(symbol) # RECORD IT
                        matches_found += 1
                
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue

        logger.info(f"🏁 Scan Complete. Found {matches_found} new setups.")

def main():
    # Only run during market hours (Simple Local Check)
    now = datetime.now()
    if now.weekday() >= 5: # Saturday/Sunday
        logger.info("😴 Weekend - Scanner resting.")
        return

    try:
        scanner = OmkarTradeDesk()
        scanner.execute_scan()
    except Exception as e:
        logger.critical(f"Critical System Failure: {e}")

if __name__ == "__main__":
    main()
