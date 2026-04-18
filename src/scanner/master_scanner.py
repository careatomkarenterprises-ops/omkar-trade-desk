import pandas as pd
import json
import os
from datetime import datetime
from src.scanner.volume_analyzer import VolumeSetupAnalyzer
from src.scanner.data_fetcher import fetch_historical_data
from src.telegram.poster import send_alert, send_delayed_alert

class MasterScanner:
    def __init__(self):
        self.analyzer = VolumeSetupAnalyzer(volume_period=15, sma_period=15)
        self.cache_file = "data/last_scanner_cache.json"

    # ---------- 1. Morning Pre-Market Gap (Daily chart) ----------
    def scan_premarket_gap(self):
        df = fetch_historical_data("NIFTY", interval="daily", days=20)
        if df is None or df.empty:
            return
        setups = self.analyzer.detect_setups(df)
        if not setups:
            msg = "🌅 Pre-Market: No significant volume setup detected. Neutral observation."
            send_alert(msg, "@OmkarFree")
            return
        latest = setups[-1]
        global_sentiment = self._get_global_sentiment()
        current_futures = self._get_current_futures_price()
        bias = "Upward bias" if current_futures > latest['top'] else ("Downward bias" if current_futures < latest['bottom'] else "Sideways")
        msg = (f"🌅 *Pre-Market Observation*\n"
               f"📊 Volume setup: {latest['candles']} high-volume candles\n"
               f"📐 Observed range: {latest['bottom']} – {latest['top']}\n"
               f"🎯 Statistical zone (FAB 50%): {latest['fab_50']}\n"
               f"🌍 Global cues: {global_sentiment}\n"
               f"📈 {bias}\n⚠️ Educational purpose only.")
        send_alert(msg, "@OmkarFree")

    # ---------- 2. Pre-Open Top/Bottom Stocks (30-min chart) ----------
    def scan_preopen_top_bottom(self):
        # Get top/bottom stocks from pre-open data (requires Zerodha API)
        # For now, we simulate with a list of popular stocks; replace with actual API call.
        top_bottom_list = self._get_preopen_list()  # implement based on your data source
        results = []
        for symbol in top_bottom_list[:20]:
            df = fetch_historical_data(symbol, interval="30minute", days=5)
            if df is None or df.empty:
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
            msg = "📊 *Pre-Open Stock Patterns*\n" + "\n".join(results) + "\n⚠️ Educational observation."
        else:
            msg = "📊 Pre-Open: No qualifying volume setups found."
        send_alert(msg, "@OmkarFree")

    # ---------- 3. After-Open F&O + Index (3-min, min_candles=6) ----------
    def scan_intraday_fno(self, channel="@OmkarPro"):
        symbols = self._get_fno_list() + ["NIFTY", "BANKNIFTY"]
        self.analyzer.min_candles = 6
        alerts = []
        for symbol in symbols:
            df = fetch_historical_data(symbol, interval="3minute", days=2)
            if df is None or df.empty:
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
                       f"📏 Range: {latest['range']}\n⚠️ Educational observation.")
                send_alert(msg, channel)   # premium gets real-time
                alerts.append({"symbol": symbol, "setup": latest, "price": current})
        # Cache for delayed free posting
        self._cache_alerts(alerts)
        self.analyzer.min_candles = 5

    # ---------- 4 & 5. Multibagger (Daily, min_candles=6, breakout with low volume) ----------
    def scan_multibagger(self, asset_list, name="Multibagger", channel="@OmkarProElite"):
        self.analyzer.min_candles = 6
        results = []
        for symbol in asset_list[:100]:  # limit to 100 for performance
            df = fetch_historical_data(symbol, interval="daily", days=60)
            if df is None or df.empty:
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
            msg = f"📈 *{name} Candidates (Weekly/Monthly)*\n" + "\n".join(results[:10]) + "\n⚠️ Educational screening."
            send_alert(msg, channel)
        self.analyzer.min_candles = 5

    # ---------- 7. Currency (3-min, min_candles=5) ----------
    def scan_currency(self, channel="@OmkarPro"):
        pairs = ["USDINR", "EURINR", "GBPINR", "JPYINR"]
        for pair in pairs:
            df = fetch_historical_data(pair, interval="3minute", days=2)
            if df is None or df.empty:
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
            send_alert(msg, channel)

    # ---------- 8. Commodity (3-min + Daily) ----------
    def scan_commodity(self, channel="@OmkarPro"):
        commodities = ["GOLD", "SILVER", "CRUDEOIL", "NATURALGAS"]
        for comm in commodities:
            msg = f"🛢️ *Commodity Observation* – {comm}\n"
            # Intraday 3-min
            df_intra = fetch_historical_data(comm, interval="3minute", days=2)
            if df_intra is not None and not df_intra.empty:
                setups = self.analyzer.detect_setups(df_intra)
                if setups:
                    s = setups[-1]
                    msg += f"📊 Intraday range: {s['bottom']} – {s['top']}\n"
            # Daily positional
            df_daily = fetch_historical_data(comm, interval="daily", days=30)
            if df_daily is not None and not df_daily.empty:
                setups = self.analyzer.detect_setups(df_daily)
                if setups:
                    s = setups[-1]
                    msg += f"📈 Daily statistical zone: {s['fab_50']}\n"
            if "Intraday range" in msg or "statistical zone" in msg:
                msg += "⚠️ Educational only."
                send_alert(msg, channel)

    # ---------- Helper methods (implement according to your data sources) ----------
    def _get_global_sentiment(self):
        # TODO: fetch SGX Nifty, Dow Futures, Asian markets
        # For now return a placeholder
        return "Mixed (use live data)"

    def _get_current_futures_price(self):
        # TODO: use Zerodha API to get Nifty futures price
        return 24500  # placeholder

    def _get_preopen_list(self):
        # TODO: get actual top/bottom gainers/losers from pre-market data
        # Example: return ["RELIANCE", "TCS", "INFY", "HDFC", "ICICIBANK"]
        return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    def _get_fno_list(self):
        # Read from your fno_stocks.csv
        try:
            df = pd.read_csv("fno_stocks.csv")
            return df['symbol'].tolist()
        except:
            return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    def _cache_alerts(self, alerts):
        """Store alerts for delayed free posting"""
        data = {"timestamp": datetime.now().isoformat(), "alerts": alerts}
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)

# Entry point for GitHub Actions
if __name__ == "__main__":
    scanner = MasterScanner()
    scanner.scan_premarket_gap()
    scanner.scan_preopen_top_bottom()
    scanner.scan_intraday_fno(channel="@OmkarPro")   # real-time to premium
    scanner.scan_multibagger(scanner._get_fno_list(), "F&O Multibagger", "@OmkarProElite")
    # Optional: scan all NSE stocks (if you have a list)
    # scanner.scan_multibagger(all_nse_symbols, "All Stocks Multibagger", "@OmkarProElite")
    scanner.scan_currency()
    scanner.scan_commodity()
