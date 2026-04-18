import pandas as pd
import json
import os
import logging
from datetime import datetime
from src.scanner.volume_analyzer import VolumeSetupAnalyzer
from src.telegram.poster import send_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterScanner:
    def __init__(self):
        self.analyzer = VolumeSetupAnalyzer(volume_period=15, sma_period=15)
        self.cache_file = "data/last_scanner_cache.json"
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

    def _safe_fetch(self, symbol, interval, days=5):
        """Safely fetch data without crashing"""
        try:
            from src.scanner.data_fetcher import fetch_historical_data
            df = fetch_historical_data(symbol, interval=interval, days=days)
            if df is None or df.empty:
                logger.warning(f"No data for {symbol} {interval}")
                return None
            return df
        except Exception as e:
            logger.error(f"Fetch error {symbol}: {e}")
            return None

    # ---------- 1. Morning Pre-Market Gap ----------
    def scan_premarket_gap(self):
        try:
            df = self._safe_fetch("NIFTY", "daily", 20)
            if df is None:
                raise Exception("No NIFTY data")
            setups = self.analyzer.detect_setups(df)
            if not setups:
                msg = "🌅 Pre-Market: No significant volume setup detected."
            else:
                latest = setups[-1]
                global_sentiment = self._get_global_sentiment()
                current_futures = self._get_current_futures_price()
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
            logger.error(f"Pre-market scan failed: {e}")
            send_message("free_main", f"⚠️ Pre-market scan error: {str(e)[:100]}")

    # ---------- 2. Pre-Open Top/Bottom Stocks ----------
    def scan_preopen_top_bottom(self):
        try:
            top_bottom_list = self._get_preopen_list()
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
                    side = "trading above observed resistance"
                elif current < latest['bottom']:
                    side = "trading below observed support"
                else:
                    side = "inside observed range"
                results.append(f"• {symbol}: {side} (range {latest['bottom']}-{latest['top']})")
            if results:
                msg = "📊 *Pre-Open Stock Patterns*\n" + "\n".join(results) + "\n⚠️ Educational."
            else:
                msg = "📊 Pre-Open: No qualifying volume setups."
            send_message("free_main", msg)
            logger.info("Pre-open scan completed")
        except Exception as e:
            logger.error(f"Pre-open scan failed: {e}")

    # ---------- 3. Intraday F&O (real-time to premium) ----------
    def scan_intraday_fno(self):
        try:
            symbols = self._get_fno_list() + ["NIFTY", "BANKNIFTY"]
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
                    alerts.append({"symbol": symbol, "setup": latest, "price": current})
            self._cache_alerts(alerts)
            self.analyzer.min_candles = 5
            logger.info(f"Intraday F&O scan completed, {len(alerts)} alerts")
        except Exception as e:
            logger.error(f"Intraday scan failed: {e}")

    # ---------- 4. Multibagger ----------
    def scan_multibagger(self, asset_list, name="Multibagger"):
        try:
            self.analyzer.min_candles = 6
            results = []
            for symbol in asset_list[:100]:
                df = self._safe_fetch(symbol, "daily", 60)
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
                    results.append(f"• {symbol}: breakout above {latest['top']} on below-average volume")
            if results:
                msg = f"📈 *{name} Candidates*\n" + "\n".join(results[:10]) + "\n⚠️ Educational."
                send_message("premium_elite", msg)
            self.analyzer.min_candles = 5
            logger.info(f"Multibagger scan completed, {len(results)} candidates")
        except Exception as e:
            logger.error(f"Multibagger scan failed: {e}")

    # ---------- 5. Currency ----------
    def scan_currency(self):
        try:
            pairs = ["USDINR", "EURINR", "GBPINR", "JPYINR"]
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
            logger.info("Currency scan completed")
        except Exception as e:
            logger.error(f"Currency scan failed: {e}")

    # ---------- 6. Commodity ----------
    def scan_commodity(self):
        try:
            commodities = ["GOLD", "SILVER", "CRUDEOIL", "NATURALGAS"]
            for comm in commodities:
                msg = f"🛢️ *Commodity Observation* – {comm}\n"
                df_intra = self._safe_fetch(comm, "3minute", 2)
                if df_intra is not None:
                    setups = self.analyzer.detect_setups(df_intra)
                    if setups:
                        s = setups[-1]
                        msg += f"📊 Intraday range: {s['bottom']} – {s['top']}\n"
                df_daily = self._safe_fetch(comm, "daily", 30)
                if df_daily is not None:
                    setups = self.analyzer.detect_setups(df_daily)
                    if setups:
                        s = setups[-1]
                        msg += f"📈 Daily statistical zone: {s['fab_50']}\n"
                if "Intraday range" in msg or "statistical zone" in msg:
                    msg += "⚠️ Educational only."
                    send_message("premium", msg)
            logger.info("Commodity scan completed")
        except Exception as e:
            logger.error(f"Commodity scan failed: {e}")

    # ---------- Helpers ----------
    def _get_global_sentiment(self):
        # Implement with yfinance or fallback
        return "Neutral (live data not configured)"

    def _get_current_futures_price(self):
        # Use a fallback value – in production, fetch from Zerodha
        return 24500

    def _get_preopen_list(self):
        # Replace with actual pre-open gainers/losers from your data source
        return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    def _get_fno_list(self):
        try:
            if os.path.exists("fno_stocks.csv"):
                df = pd.read_csv("fno_stocks.csv")
                if 'symbol' in df.columns:
                    return df['symbol'].tolist()
            return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        except:
            return ["RELIANCE", "TCS", "INFY"]

    def _cache_alerts(self, alerts):
        data = {"timestamp": datetime.now().isoformat(), "alerts": alerts}
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)

if __name__ == "__main__":
    scanner = MasterScanner()
    scanner.scan_premarket_gap()
    scanner.scan_preopen_top_bottom()
    scanner.scan_intraday_fno()
    scanner.scan_multibagger(scanner._get_fno_list(), "F&O Multibagger")
    scanner.scan_currency()
    scanner.scan_commodity()
    logger.info("All scanners executed")
