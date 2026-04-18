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

    # ---------- 1. Morning Pre-Market Gap (Nifty) ----------
    def scan_premarket_gap(self):
        try:
            # NOTE: Zerodha expects interval "day" not "daily"
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
                # TODO: replace with real futures price from Zerodha if needed
                current_futures = 24500
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
            # Use NSE prefix for equities (adjust if your ZerodhaFetcher expects plain symbols)
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

    # ---------- 3. Intraday F&O + Index (3-min, real-time to premium) ----------
    def scan_intraday_fno(self):
        try:
            symbols = self._get_fno_list() + ["NSE:NIFTY 50", "NSE:BANK NIFTY"]
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
                df = self._safe_fetch(symbol, "day", 60)   # "day" not "daily"
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

    # ---------- 5. Currency (3-min) ----------
    def scan_currency(self):
        try:
            # CDS exchange for currency derivatives
            pairs = ["CDS:USDINR", "CDS:EURINR", "CDS:GBPINR", "CDS:JPYINR"]
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

    # ---------- 6. Commodity (3-min + daily) ----------
    def scan_commodity(self):
        try:
            # MCX exchange for commodities
            commodities = ["MCX:GOLD", "MCX:SILVER", "MCX:CRUDEOIL", "MCX:NATURALGAS"]
            for comm in commodities:
                msg = f"🛢️ *Commodity* – {comm}\n"
                df_intra = self._safe_fetch(comm, "3minute", 2)
                if df_intra is not None:
                    setups = self.analyzer.detect_setups(df_intra)
                    if setups:
                        s = setups[-1]
                        msg += f"📊 Intraday range: {s['bottom']} – {s['top']}\n"
                df_daily = self._safe_fetch(comm, "day", 30)   # "day" not "daily"
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
                    # Return raw symbols; your zerodha_fetcher will map to tokens
                    return df['symbol'].tolist()[:50]
        except Exception as e:
            logger.error(f"Error reading fno_stocks.csv: {e}")
        # Fallback with NSE prefix
        return ["NSE:RELIANCE", "NSE:TCS", "NSE:INFY", "NSE:HDFCBANK", "NSE:ICICIBANK"]

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
