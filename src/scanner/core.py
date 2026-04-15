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

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ---------------- MAIN ENGINE ----------------
class OmkarTradeDesk:

    def __init__(self):
        logger.info("🚀 Initializing Omkar Trade Intelligence Engine...")

        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.poster = TelegramPoster()

        self.symbols_file = 'fno_stocks.csv'
        self.history_file = 'data/sent_alerts.json'
        os.makedirs('data', exist_ok=True)

        self.sent_alerts = self._load_history()

    # ---------------- HISTORY SYSTEM ----------------
    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)

                if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                    return data.get('symbols', [])

            except Exception as e:
                logger.error(f"History load error: {e}")

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
                logger.error(f"History save error: {e}")

    # ---------------- UNIVERSE ----------------
    def get_symbols(self):
        try:
            if os.path.exists(self.symbols_file):
                df = pd.read_csv(self.symbols_file)
                return df['symbol'].tolist()

            return ["RELIANCE", "TCS", "HDFCBANK", "INFY"]

        except Exception as e:
            logger.error(f"Symbol load error: {e}")
            return []

    # ---------------- SCORING ENGINE ----------------
    def calculate_score(self, result):
        """
        Converts pattern result into strength score (0–100)
        """
        score = 0

        if result.get("has_pattern"):
            score += 40

        score += min(result.get("surge_ratio", 1) * 10, 25)

        strength = result.get("strength", 0)
        score += strength * 35

        return min(int(score), 100)

    # ---------------- MAIN SCAN ----------------
    def execute_scan(self):

        if not self.fetcher.is_ready():
            logger.warning("⚠ Market not ready or API disconnected")
            return False

        logger.info("📡 Starting Market Intelligence Scan...")

        symbols = self.get_symbols()
        matches_found = 0

        for symbol in symbols:

            if symbol in self.sent_alerts:
                continue

            try:
                logger.info(f"🔍 Scanning: {symbol}")

                data = self.fetcher.get_stock_data(symbol)

                if data is None or data.empty:
                    continue

                result = self.detector.analyze(symbol, data)

                if not result or not result.get('has_pattern'):
                    continue

                # ---------------- SCORE ----------------
                score = self.calculate_score(result)
                result["score"] = score

                logger.info(f"📊 Signal Detected: {symbol} | Score: {score}")

                # ---------------- MESSAGE ----------------
                message = (
                    f"📊 MARKET INTELLIGENCE ALERT\n\n"
                    f"🎫 Symbol: {symbol}\n"
                    f"🔍 Setup: {result.get('trigger','Pattern Detected')}\n"
                    f"💰 Price: ₹{result.get('price')}\n"
                    f"📦 Range: {result.get('support')} - {result.get('resistance')}\n"
                    f"📊 Volume Surge: {result.get('surge_ratio')}x\n"
                    f"⭐ Strength Score: {score}/100\n\n"
                    f"⚠ This is a market condition alert, not a recommendation."
                )

                # ---------------- SAVE SIGNAL ----------------
                with open("data/latest_signal.json", "w") as f:
                    json.dump(result, f, indent=2)

                # ---------------- CHANNEL LOGIC ----------------
                self.poster.send_message("free", message)

                if score >= 75:
                    self.poster.send_message("premium", message)

                # ---------------- HISTORY ----------------
                self._save_history(symbol)
                matches_found += 1

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")

        logger.info(f"🏁 Scan Complete | Total Signals: {matches_found}")
        return True


# ---------------- HOLIDAY FUNCTION ----------------
def send_holiday_wish(occasion, poster):

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    if now.hour == 9 and now.minute <= 35:

        msg = (
            f"✨ MARKET CLOSED NOTICE ✨\n\n"
            f"Happy {occasion}\n\n"
            f"Market is closed today.\n"
            f"Scanner will resume next session.\n\n"
            f"Omkar Trade Intelligence System"
        )

        poster.send_message("free", msg)


# ---------------- MAIN ENTRY ----------------
def main():

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    today = now.strftime('%Y-%m-%d')

    holidays = {
        "2026-01-26": "Republic Day",
        "2026-03-03": "Holi",
        "2026-04-14": "Ambedkar Jayanti",
        "2026-05-01": "Maharashtra Day",
        "2026-10-02": "Gandhi Jayanti"
    }

    # Weekend block
    if now.weekday() >= 5:
        logger.info("⏳ Weekend - System idle")
        return

    # Holiday block
    if today in holidays:
        poster = TelegramPoster()
        send_holiday_wish(holidays[today], poster)
        return

    try:
        scanner = OmkarTradeDesk()
        success = scanner.execute_scan()

        if not success:
            scanner.poster.send_message(
                "free",
                "⚠ Market not active or API issue. No scans executed."
            )

    except Exception as e:
        logger.critical(f"System failure: {e}")


if __name__ == "__main__":
    main()
