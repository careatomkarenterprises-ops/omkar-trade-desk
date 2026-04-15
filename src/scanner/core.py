import os
import logging
import pandas as pd
import time
import json
from datetime import datetime
import pytz

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
        
        self.sent_alerts = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                        return data.get('symbols', [])
            except Exception as e:
                logger.error(f"Error loading history: {e}")
        return []

    def _save_history(self, symbol):
        if symbol not in self.sent_alerts:
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
            logger.warning("Market might be closed or API is disconnected.")
            return False 

        logger.info("🚀 Starting Market Scan...")
        symbols = self.get_fno_symbols()
        matches_found = 0

        for symbol in symbols:
            if symbol in self.sent_alerts:
                continue

            try:
                logger.info(f"Checking symbol: {symbol}")

                data = self.fetcher.get_stock_data(symbol) 
                
                if data is not None and not data.empty:
                    result = self.detector.analyze(symbol, data)

                    logger.info(f"Analysis result: {result}")
                    
                    if result and result.get('has_pattern'):
                        logger.info(f"✅ Pattern Found: {symbol}")
                        
                        message = (
                            f"🔍 {result['trigger']}\n\n"
                            f"🎫 Symbol: {symbol}\n"
                            f"💰 Price: ₹{result['price']}\n"
                            f"📊 Volume Surge: {result['surge_ratio']}x\n"
                            f"📦 Range: {result['support']} - {result['resistance']}\n"
                            f"⚡ Strength: {'⭐' * int(result['strength'] * 5)}"
                        )

                        # ✅ SAVE SIGNAL (VERY IMPORTANT)
                        with open("data/latest_signal.json", "w") as f:
                            json.dump(result, f, indent=2)

                        # ✅ SEND TO FREE CHANNEL
                        self.poster.send_message("free", message)

                        # ✅ SEND TO PREMIUM IF STRONG
                        if result.get('strength', 0) > 0.7:
                            self.poster.send_message("premium", message)

                        self._save_history(symbol)
                        matches_found += 1
                
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue

        logger.info(f"🏁 Scan Complete. Found {matches_found} setups.")
        return True


def send_holiday_wish(occasion, poster):
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    if now.hour == 9 and now.minute <= 35:
        wish_msg = (
            f"✨ Greetings from Omkar TradeDesk ✨\n\n"
            f"Happy {occasion}\n\n"
            f"Market is closed today.\n"
            f"Scans will resume next trading day.\n\n"
            f"Omkar Team"
        )
        poster.send_message("free", wish_msg)


def main():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    today_str = now.strftime('%Y-%m-%d')

    holidays = {
        "2026-01-26": "Republic Day",
        "2026-03-03": "Holi",
        "2026-04-14": "Ambedkar Jayanti",
        "2026-05-01": "Maharashtra Day",
        "2026-10-02": "Gandhi Jayanti"
    }

    if now.weekday() >= 5:
        logger.info("Weekend - System stopped.")
        return

    if today_str in holidays:
        poster = TelegramPoster()
        send_holiday_wish(holidays[today_str], poster)
        return

    try:
        scanner = OmkarTradeDesk()
        success = scanner.execute_scan()

        if not success:
            scanner.poster.send_message(
                "free",
                "Market seems closed or API issue. No signals today."
            )

    except Exception as e:
        logger.critical(f"Critical Error: {e}")


if __name__ == "__main__":
    main()
