import sys
import os
# Add repository root to path so 'src' imports work in GitHub Actions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import json
import logging
from datetime import datetime
from src.scanner.volume_analyzer import VolumeSetupAnalyzer
from src.scanner.data_fetcher import fetch_historical_data
from src.telegram.poster import send_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterScanner:
    def __init__(self):
        self.analyzer = VolumeSetupAnalyzer(volume_period=15, sma_period=15)
        self.cache_file = "data/last_scanner_cache.json"
        os.makedirs("data", exist_ok=True)

    def _safe_fetch(self, symbol, interval, days=5):
        try:
            return fetch_historical_data(symbol, interval, days)
        except Exception as e:
            logger.error(f"Fetch error {symbol}: {e}")
            return None

    # ---------- Helper: Get Nifty & Bank Nifty futures (current & next expiry) ----------
    def _get_future_symbols(self):
        """
        Returns a list of NFO symbols for Nifty and Bank Nifty futures.
        Current month + next month (or nearest two expiries).
        Uses simple logic: if current day > 20, current expiry = next month; else current month.
        """
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day

        # If after 20th of the month, the current expiry is actually next month
        if day > 20:
            curr_month = month + 1
            curr_year = year
            if curr_month > 12:
                curr_month = 1
                curr_year += 1
            next_month = curr_month + 1
            next_year = curr_year
            if next_month > 12:
                next_month = 1
                next_year += 1
        else:
            curr_month = month
            curr_year = year
            next_month = month + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1

        month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                       "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        curr_month_name = month_names[curr_month - 1]
        next_month_name = month_names[next_month - 1]

        curr_yr_suffix = str(curr_year)[-2:]
        next_yr_suffix = str(next_year)[-2:]

        nifty_curr = f"NFO:NIFTY{curr_yr_suffix}{curr_month_name}FUT"
        nifty_next = f"NFO:NIFTY{next_yr_suffix}{next_month_name}FUT"
        banknifty_curr = f"NFO:BANKNIFTY{curr_yr_suffix}{curr_month_name}FUT"
        banknifty_next = f"NFO:BANKNIFTY{next_yr_suffix}{next_month_name}FUT"

        return [nifty_curr, nifty_next, banknifty_curr, banknifty_next]

    # ---------- 1. Morning Pre-Market Gap (Nifty spot) ----------
    def scan_premarket_gap(self):
        try:
            df = self._safe_fetch("NSE:NIFTY 50", "day", 20)
            if df is None:
                send_message("free_main", "🌅 Pre-Market: Unable to fetch NIFTY data.")
                return
            setups = self.analyzer.detect_setups(df)
            if not setups:
                msg = "🌅 Pre-Market: No significant volume setup detected."
            else:
                latest = setups[-1]
                global_sentiment = "Neutral (live data not configured)"
                current_futures = 24500  # placeholder; replace with real futures price if needed
                if current_futures > latest['top']:
                    bias = "Upward bias"
                elif current_futures < latest['bottom']:
                    bias = "Downward bias"
                else:
                    bias = "Sideways"
                msg = (f"🌅 *Pre-Market Observation*\n"
                       f"📊 Volume setup: {latest['candles']} high-volume candles\n"
                       f"📐 Observed range: {latest['bottom']} – {latest['top']}\n"
                       f"🎯 Statistical zone: {latest['fab_50']}\n"
                       f"🌍 Global cues: {global_sentiment}\n"
                       f"📈 {bias}\n⚠️ Educational purpose only.")
            send_message("free_main", msg)
            logger.info("Pre-market gap scan completed")
        except Exception as e:
            logger.error(f"Pre-market scan error: {e}")

    # ---------- 2. Pre-Open Top/Bottom Stocks (30-min) ----------
    def scan_preopen_top_bottom(self):
        try:
            top_bottom_list = ["NSE:RELIANCE", "NSE:TCS", "NSE:INFY", "NSE:HDFCBANK", "NSE:ICICIBANK"]
            results = []
            for symbol in top_bottom_list[:20]:
                df = self._safe_fetch(symbol, "30minute", 5)
                if df is None:
                    continue
                setups = self.analyzer.detect_setups(df)
                if not setups:
                    continue
                latest = setups[-1]
                current = df['close'].iloc[-1]
                if current > latest['top']:
                    side = "above observed resistance"
                elif current < latest['bottom']:
                    side = "below observed support"
                else:
                    side = "inside observed range"
                results.append(f"• {symbol}: {side} (range {latest['bottom']}-{latest['top']})")
            if results:
                msg = "📊 *Pre-Open Stock Patterns*\n" + "\n".join(results) + "\n⚠️ Educational."
            else:
                msg = "📊 Pre-Open: No qualifying volume setups."
            send_message("free_main", msg)
        except Exception as e:
            logger.error(f"Pre-open error: {e}")

    # ---------- 3. Intraday F&O + Index Futures (3-min, real-time to premium) ----------
    def scan_intraday_fno(self):
        try:
            # Get futures symbols for Nifty & Bank Nifty (current + next)
            future_symbols = self._get_future_symbols()
            # Regular F&O stocks (from CSV, plain symbols)
            stock_symbols = self._get_fno_list()
            symbols = stock_symbols + future_symbols

            self.analyzer.min_candles = 6
            alerts = []
            for symbol in symbols:
                df = self._safe_fetch(symbol, "3minute", 2)
                if df is None:
                    continue
                setups = self.analyzer.detect_setups(df)
                if not setups:
                    continue
                latest = setups[-1]
                current = df['close'].iloc[-1]
                sma_cross = self.analyzer.check_sma_crossover(df)
                if current > latest['top'] and sma_cross:
                    msg = (f"📊 *Intraday Pattern* – {symbol}\n"
                           f"📈 Setup: {latest['candles']} high-volume candles\n"
                           f"🔴 Upper bound: {latest['top']}\n"
                           f"🟢 Lower bound: {latest['bottom']}\n"
                           f"🎯 Statistical zone: {latest['fab_50']}\n"
                           f"📏 Range: {latest['range']}\n⚠️ Educational.")
                    send_message("premium", msg)
                    alerts.append({"symbol": symbol, "setup": latest})
            self._cache_alerts(alerts)
            self.analyzer.min_candles = 5
        except Exception as e:
            logger.error(f"Intraday error: {e}")

    # ---------- 4. Multibagger (Daily, min 6 candles, low-volume breakout) ----------
    def scan_multibagger(self, asset_list, name="Multibagger"):
        try:
            self.analyzer.min_candles = 6
            results = []
            for symbol in asset_list[:100]:
                df = self._safe_fetch(symbol, "day", 60)
                if df is None:
                    continue
                setups = self.analyzer.detect_setups(df)
                if not setups:
                    continue
                latest = setups[-1]
                last_close = df['close'].iloc[-1]
                last_volume = df['volume'].iloc[-1]
                avg_volume = df['volume'].rolling(15).mean().iloc[-1]
                if last_close > latest['top'] and last_volume < avg_volume:
                    results.append(f"• {symbol}: breakout above {latest['top']} on low volume")
            if results:
                msg = f"📈 *{name} Candidates*\n" + "\n".join(results[:10]) + "\n⚠️ Educational."
                send_message("premium_elite", msg)
            self.analyzer.min_candles = 5
        except Exception as e:
            logger.error(f"Multibagger error: {e}")

    # ---------- 5. Currency (3-min) – using NSE spot rates ----------
    def scan_currency(self):
        try:
            pairs = ["NSE:USDINR", "NSE:EURINR", "NSE:GBPINR", "NSE:JPYINR"]
            for pair in pairs:
                df = self._safe_fetch(pair, "3minute", 2)
                if df is None:
                    continue
                setups = self.analyzer.detect_setups(df)
                if not setups:
                    continue
                latest = setups[-1]
                current = df['close'].iloc[-1]
                if current > latest['top']:
                    bias = "upward bias"
                elif current < latest['bottom']:
                    bias = "downward bias"
                else:
                    bias = "sideways"
                msg = (f"💱 *Currency Pattern* – {pair}\n"
                       f"📊 Setup: {latest['candles']} candles\n"
                       f"📐 Range: {latest['bottom']} – {latest['top']}\n"
                       f"📈 {bias}\n⚠️ Educational.")
                send_message("premium", msg)
        except Exception as e:
            logger.error(f"Currency error: {e}")

    # ---------- 6. Commodity (3-min + daily) – corrected MCX symbols ----------
    def scan_commodity(self):
        try:
            commodities = ["MCX:GOLD1", "MCX:SILVER1", "MCX:CRUDEOIL1", "MCX:NATGAS1"]
            for comm in commodities:
                msg = f"🛢️ *Commodity* – {comm}\n"
                df_intra = self._safe_fetch(comm, "3minute", 2)
                if df_intra is not None:
                    setups = self.analyzer.detect_setups(df_intra)
                    if setups:
                        s = setups[-1]
                        msg += f"📊 Intraday range: {s['bottom']} – {s['top']}\n"
                df_daily = self._safe_fetch(comm, "day", 30)
                if df_daily is not None:
                    setups = self.analyzer.detect_setups(df_daily)
                    if setups:
                        s = setups[-1]
                        msg += f"📈 Daily statistical zone: {s['fab_50']}\n"
                if "Intraday range" in msg or "statistical zone" in msg:
                    msg += "⚠️ Educational."
                    send_message("premium", msg)
        except Exception as e:
            logger.error(f"Commodity error: {e}")

    # ---------- Helpers ----------
    def _get_fno_list(self):
        try:
            if os.path.exists("fno_stocks.csv"):
                df = pd.read_csv("fno_stocks.csv")
                if 'symbol' in df.columns:
                    return df['symbol'].tolist()[:50]
        except Exception as e:
            logger.error(f"Error reading fno_stocks.csv: {e}")
        return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    def _cache_alerts(self, alerts):
        with open(self.cache_file, 'w') as f:
            json.dump({"timestamp": datetime.now().isoformat(), "alerts": alerts}, f)

if __name__ == "__main__":
    scanner = MasterScanner()
    scanner.scan_premarket_gap()
    scanner.scan_preopen_top_bottom()
    scanner.scan_intraday_fno()
    scanner.scan_multibagger(scanner._get_fno_list(), "F&O Multibagger")
    scanner.scan_currency()
    scanner.scan_commodity()
    logger.info("All scanners executed successfully")
