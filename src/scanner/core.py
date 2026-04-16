import os
import logging
import pandas as pd
import time
import json
from datetime import datetime
import pytz

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.scanner.smart_money_filter import SmartMoneyFilter
from src.telegram.poster import TelegramPoster


# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =========================================================
# 🚀 OMKAR TRADE INTELLIGENCE ENGINE (PRODUCTION)
# =========================================================
class OmkarTradeDesk:

    def __init__(self):
        logger.info("🚀 Initializing Omkar Institutional Scanner...")

        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.smart_filter = SmartMoneyFilter()
        self.poster = TelegramPoster()

        self.symbols_file = 'fno_stocks.csv'
        self.history_file = 'data/sent_alerts.json'

        os.makedirs('data', exist_ok=True)

        self.sent_alerts = self._load_history()

    # ---------------- HISTORY ----------------
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

    # ---------------- SYMBOL UNIVERSE ----------------
    def get_symbols(self):
        try:
            if os.path.exists(self.symbols_file):
                df = pd.read_csv(self.symbols_file)
                return df['symbol'].tolist()

            return ["RELIANCE", "TCS", "HDFCBANK", "INFY"]

        except Exception as e:
            logger.error(f"Symbol load error: {e}")
            return []

    # ---------------- SCORE ENGINE ----------------
    def calculate_score(self, pattern_result, smart_result):
        """
        FINAL INSTITUTIONAL SCORING MODEL
        """

        base = 0

        # Pattern strength
        base += pattern_result.get("strength", 0) * 50

        # Volume surge impact
        base += min(pattern_result.get("surge_ratio", 1) * 8, 30)

        # Smart money confirmation
        base += smart_result.get("score", 0) * 40

        return min(int(base), 100)

    # ---------------- MAIN SCAN ----------------
    def execute_scan(self):

        if not self.fetcher.is_ready():
            logger.warning("⚠ Market not ready or API disconnected")
            return False

        logger.info("📡 Starting Institutional Market Scan...")

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

                # =========================
                # 1. PATTERN ENGINE
                # =========================
                pattern_result = self.detector.analyze(symbol, data)

                if not pattern_result or not pattern_result.get('has_pattern'):
                    continue

                # =========================
                # 2. SMART MONEY FILTER
                # =========================
                smart_result = self.smart_filter.is_institutional_move(data)

                if not smart_result.get("valid"):
                    logger.info(f"❌ Rejected Smart Money Filter: {symbol}")
                    continue

                # =========================
                # 3. FINAL SCORE
                # =========================
                score = self.calculate_score(pattern_result, smart_result)

                pattern_result["score"] = score
                pattern_result["smart_score"] = smart_result["score"]

                logger.info(f"📊 SIGNAL: {symbol} | SCORE: {score}")

                # =========================
                # 4. TELEGRAM MESSAGE
                # =========================message = (
    f"📊 INSTITUTIONAL OPTIONS INTELLIGENCE ALERT\n\n"
    f"🎫 Symbol: {symbol}\n"
    f"🔍 Setup: {pattern_result.get('trigger','Detected')}\n"
    f"💰 Price: ₹{pattern_result.get('price')}\n"
    f"📦 Support: {pattern_result.get('support')} | Resistance: {pattern_result.get('resistance')}\n"
    f"📊 Volume Surge: {pattern_result.get('surge_ratio')}x\n\n"
    
    f"🧠 Smart Money Score: {smart_result.get('score')}\n"
    f"📈 Pattern Strength: {pattern_result.get('strength')}\n"
    f"⭐ Final Score: {score}/100\n\n"

    f"⚠ IMPORTANT DISCLOSURE:\n"
    f"This is a MARKET STRUCTURE ALERT generated by an automated system.\n"
    f"It is NOT a recommendation to buy or sell any security.\n"
    f"Please do your own analysis before any decision.\n\n"

    f"🏛 Omkar Institutional Market Intelligence System"
)

                # =========================
                # 5. SAVE SIGNAL
                # =========================
                with open("data/latest_signal.json", "w") as f:
                    json.dump({
                        "pattern": pattern_result,
                        "smart_money": smart_result,
                        "final_score": score,
                        "symbol": symbol,
                        "time": str(datetime.now())
                    }, f, indent=2)

                # =========================
                # 6. SEND TELEGRAM
                # =========================
                self.poster.send_message("free", message)

                if score >= 75:
                    self.poster.send_message("premium", message)

                # =========================
                # 7. HISTORY UPDATE
                # =========================
                self._save_history(symbol)
                matches_found += 1

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")

        logger.info(f"🏁 SCAN COMPLETE | SIGNALS: {matches_found}")
        return True


# ---------------- HOLIDAY ----------------
def send_holiday_wish(occasion, poster):

    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    if now.hour == 9 and now.minute <= 35:

        msg = (
            f"✨ MARKET CLOSED NOTICE ✨\n\n"
            f"Happy {occasion}\n\n"
            f"Market is closed today.\n"
            f"Scanner will resume next session.\n"
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

    if now.weekday() >= 5:
        logger.info("⏳ Weekend - System idle")
        return

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
                "⚠ Market inactive or API issue detected"
            )

    except Exception as e:
        logger.critical(f"System failure: {e}")


if __name__ == "__main__":
    main()
