import sys
import os
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
        self.delayed_cache_file = "data/delayed_patterns_cache.json"
        os.makedirs("data", exist_ok=True)

    # ---------------- SAFE FETCH ----------------
    def _safe_fetch(self, symbol, interval, days=5):
        try:
            df = fetch_historical_data(symbol, interval, days)
            if df is None or df.empty:
                logger.warning(f"No data for {symbol}")
                return None
            return df
        except Exception as e:
            logger.error(f"Fetch error {symbol}: {e}")
            return None

    # ---------------- TELEGRAM ----------------
    def _send_safe(self, channel, msg):
        try:
            send_message(channel, msg)
            logger.info(f"Sent message to {channel}")
        except Exception as e:
            logger.error(f"Telegram send failed ({channel}): {e}")

    def _send_to_all_premium(self, msg):
        self._send_safe("premium", msg)
        self._send_safe("premium_elite", msg)

    # ---------------- CACHE ----------------
    def _cache_delayed_pattern(self, symbol, setup, current_price):
        try:
            if os.path.exists(self.delayed_cache_file):
                with open(self.delayed_cache_file, 'r') as f:
                    cache = json.load(f)
            else:
                cache = []
        except:
            cache = []

        cache.append({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "setup": setup,
            "price": current_price
        })

        cache = cache[-50:]

        with open(self.delayed_cache_file, 'w') as f:
            json.dump(cache, f, indent=2)

    # ---------------- SYMBOL LIST ----------------
    def _get_fno_list(self):
        return [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "SBIN.NS", "LT.NS", "AXISBANK.NS", "KOTAKBANK.NS", "ITC.NS",
            "HINDUNILVR.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "MARUTI.NS",
            "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
            "POWERGRID.NS", "NTPC.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS",
            "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "ONGC.NS",
            "COALINDIA.NS", "JSWSTEEL.NS", "TATASTEEL.NS",
            "ADANIPORTS.NS", "ADANIENT.NS"
        ]

    def _get_index_symbols(self):
        return ["^NSEI", "^NSEBANK"]

    def _get_commodity_symbols(self):
        return ["GC=F", "SI=F", "CL=F"]

    # ---------------- PREMARKET ----------------
    def scan_premarket_gap(self):
        logger.info("Running premarket scan...")

        df = self._safe_fetch("^NSEI", "day", 20)

        if df is None:
            self._send_safe("free_main", "❌ NIFTY data not available")
            return

        setups = self.analyzer.detect_setups(df)

        if not setups:
            msg = "🌅 No strong premarket setup"
        else:
            s = setups[-1]
            msg = f"""🌅 *PRE-MARKET VIEW*

Range: {s['bottom']} - {s['top']}
Zone: {s['fab_50']}

Bias: Sideways
⚠️ Educational"""

        self._send_safe("free_main", msg)

    # ---------------- INTRADAY ----------------
    def scan_intraday_fno(self):
        logger.info("Running intraday FNO scan...")

        symbols = self._get_fno_list()
        found_signal = False

        for symbol in symbols:

            logger.info(f"Checking {symbol}")

            df = self._safe_fetch(symbol, "5minute", 5)

            if df is None:
                continue

            setups = self.analyzer.detect_setups(df)

            if not setups:
                continue

            latest = setups[-1]
            current = df['close'].iloc[-1]

            logger.info(f"{symbol} | Price: {current} | Top: {latest['top']}")

            if current > latest['top']:
                found_signal = True

                msg = f"""📊 *BREAKOUT ALERT*

{symbol}

Range: {latest['bottom']} - {latest['top']}
Zone: {latest['fab_50']}

⚠️ Educational"""

                self._send_to_all_premium(msg)
                self._cache_delayed_pattern(symbol, latest, current)

        if not found_signal:
            self._send_safe("free_main", "📊 No breakout signals found in this scan")

    # ---------------- INDEX ----------------
    def scan_index(self):
        logger.info("Running index scan...")

        for idx in self._get_index_symbols():

            df = self._safe_fetch(idx, "5minute", 5)

            if df is None:
                continue

            change = ((df['close'].iloc[-1] - df['open'].iloc[0]) / df['open'].iloc[0]) * 100

            msg = f"📊 Index {idx} Move: {change:.2f}%"
            self._send_safe("free_main", msg)

    # ---------------- COMMODITY ----------------
    def scan_commodity(self):
        logger.info("Running commodity scan...")

        for comm in self._get_commodity_symbols():

            df = self._safe_fetch(comm, "5minute", 5)

            if df is None:
                continue

            msg = f"🛢️ {comm} Price: {df['close'].iloc[-1]}"
            self._send_to_all_premium(msg)

    # ---------------- DELAYED ----------------
    def post_delayed_patterns(self):
        logger.info("Posting delayed patterns...")

        if not os.path.exists(self.delayed_cache_file):
            return

        with open(self.delayed_cache_file, 'r') as f:
            cache = json.load(f)

        if not cache:
            return

        for item in cache:

            msg = f"""📊 Delayed Alert

{item['symbol']}

Range: {item['setup']['bottom']} - {item['setup']['top']}
Zone: {item['setup']['fab_50']}

⚠️ Educational"""

            self._send_safe("free_signals", msg)

        with open(self.delayed_cache_file, 'w') as f:
            json.dump([], f)


# ---------------- RUN ----------------
if __name__ == "__main__":

    scanner = MasterScanner()

    send_message("free_main", "🚀 Intraday Scanner Started")

    scanner.scan_premarket_gap()
    scanner.scan_index()
    scanner.scan_intraday_fno()
    scanner.scan_commodity()
    scanner.post_delayed_patterns()

    send_message("free_main", "✅ Scanner cycle completed")

    logger.info("✅ Scanner Completed Successfully")
