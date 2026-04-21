import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import json
import logging
import requests
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
            return fetch_historical_data(symbol, interval, days)
        except Exception as e:
            logger.error(f"Fetch error {symbol}: {e}")
            return None

    # ---------------- TELEGRAM ----------------
    def _send_to_all_premium(self, msg):
        send_message("premium", msg)
        send_message("premium_elite", msg)

    # ---------------- CACHE ----------------
    def _cache_delayed_pattern(self, symbol, setup, current_price):
        try:
            with open(self.delayed_cache_file, 'r') as f:
                cache = json.load(f)
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

    # ---------------- SYMBOL LIST (NIFTY 50 - FREE DATA SAFE) ----------------
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

    # ---------------- INDEX ----------------
    def _get_index_symbols(self):
        return ["^NSEI", "^NSEBANK"]

    # ---------------- COMMODITY (YFINANCE FORMAT) ----------------
    def _get_commodity_symbols(self):
        return ["GC=F", "SI=F", "CL=F"]  # Gold, Silver, Crude

    # ---------------- PREMARKET ----------------
    def scan_premarket_gap(self):
        df = self._safe_fetch("^NSEI", "day", 20)

        if df is None:
            send_message("free_main", "❌ NIFTY data not available")
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

        send_message("free_main", msg)

    # ---------------- INTRADAY ----------------
    def scan_intraday_fno(self):

        symbols = self._get_fno_list()

        for symbol in symbols:

            df = self._safe_fetch(symbol, "5minute", 5)

            if df is None or df.empty:
                continue

            setups = self.analyzer.detect_setups(df)

            if not setups:
                continue

            latest = setups[-1]
            current = df['close'].iloc[-1]

            if current > latest['top']:

                msg = f"""📊 *BREAKOUT ALERT*

{symbol}

Range: {latest['bottom']} - {latest['top']}
Zone: {latest['fab_50']}

⚠️ Educational"""

                self._send_to_all_premium(msg)
                self._cache_delayed_pattern(symbol, latest, current)

    # ---------------- INDEX MONITOR ----------------
    def scan_index(self):

        for idx in self._get_index_symbols():

            df = self._safe_fetch(idx, "5minute", 5)

            if df is None:
                continue

            change = ((df['close'].iloc[-1] - df['open'].iloc[0]) / df['open'].iloc[0]) * 100

            msg = f"📊 Index {idx} Move: {change:.2f}%"

            send_message("free_main", msg)

    # ---------------- COMMODITY ----------------
    def scan_commodity(self):

        for comm in self._get_commodity_symbols():

            df = self._safe_fetch(comm, "5minute", 5)

            if df is None:
                continue

            msg = f"🛢️ {comm} Price: {df['close'].iloc[-1]}"

            self._send_to_all_premium(msg)

    # ---------------- DELAYED ----------------
    def post_delayed_patterns(self):

        if not os.path.exists(self.delayed_cache_file):
            return

        with open(self.delayed_cache_file, 'r') as f:
            cache = json.load(f)

        for item in cache:

            msg = f"""📊 Delayed Alert

{item['symbol']}

Range: {item['setup']['bottom']} - {item['setup']['top']}
Zone: {item['setup']['fab_50']}

⚠️ Educational"""

            send_message("free_signals", msg)

        with open(self.delayed_cache_file, 'w') as f:
            json.dump([], f)


# ---------------- RUN ----------------
if __name__ == "__main__":

    scanner = MasterScanner()

    scanner.scan_premarket_gap()
    scanner.scan_index()
    scanner.scan_intraday_fno()
    scanner.scan_commodity()
    scanner.post_delayed_patterns()

    logger.info("✅ Scanner Completed Successfully")
