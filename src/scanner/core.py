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
        """Load the list of stocks already alerted today"""
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
        """Add a stock to today's 'already sent' list"""
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
        # 1. Check if Market is actually open via Zerodha API
        # This handles unscheduled holidays/uncertain news
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
                        self._save_history(symbol)
                        matches_found += 1
                
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue

        logger.info(f"🏁 Scan Complete. Found {matches_found} new setups.")
        return True

def send_holiday_wish(occasion, poster):
    """Sends a professional wish to members"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    # We only send the wish during the morning run (9:00 AM - 9:35 AM)
    if now.hour == 9 and now.minute <= 35:
        wish_msg = (
            f"✨ **Greetings from Omkar TradeDesk** ✨\n\n"
            f"Wishing you and your family a very Happy **{occasion}**.\n\n"
            f"🏛️ The Indian Stock Markets are closed today. Take this time to rest and recharge.\n\n"
            f"We will resume our Institutional Volume Scans on the next trading day at 9:15 AM.\n\n"
            f"Best Regards,\n"
            f"**Omkar Market Intelligence Team**"
        )
        poster.send_message(channel='premium', message=wish_msg)
        logger.info(f"🎉 Sent holiday wishes for {occasion}")

def main():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    today_str = now.strftime('%Y-%m-%d')
    
    # Official NSE Holidays 2026
    holidays = {
        "2026-01-26": "Republic Day",
        "2026-03-03": "Holi",
        "2026-03-26": "Shri Ram Navami",
        "2026-03-31": "Shri Mahavir Jayanti",
        "2026-04-03": "Good Friday",
        "2026-04-14": "Dr. Babasaheb Ambedkar Jayanti",
        "2026-05-01": "Maharashtra Day",
        "2026-05-28": "Bakri Id",
        "2026-06-26": "Muharram",
        "2026-09-14": "Ganesh Chaturthi",
        "2026-10-02": "Mahatma Gandhi Jayanti",
        "2026-10-20": "Dussehra",
        "2026-11-10": "Diwali Balipratipada",
        "2026-11-24": "Guru Nanak Jayanti",
        "2026-12-25": "Christmas"
    }

    # 1. Check for Weekend
    if now.weekday() >= 5:
        logger.info("😴 Weekend - System on standby.")
        return

    # 2. Check for Scheduled Holiday
    if today_str in holidays:
        poster = TelegramPoster()
        send_holiday_wish(holidays[today_str], poster)
        return

    # 3. Run Scanner (includes API check for unscheduled closures)
    try:
        scanner = OmkarTradeDesk()
        success = scanner.execute_scan()
        
        # If API says market is closed but it's not in our holiday list (Sudden Holiday)
        if not success and (now.hour == 9 and now.minute <= 35):
            scanner.poster.send_message(
                channel='premium', 
                message="📢 **Market Notice:** The exchange appears to be closed today for an unscheduled holiday or session change. No scans will be generated."
            )
    except Exception as e:
        logger.critical(f"Critical System Failure: {e}")

if __name__ == "__main__":
    main()
