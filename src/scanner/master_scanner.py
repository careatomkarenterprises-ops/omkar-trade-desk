import pandas as pd
import json
import os
from datetime import datetime
from src.scanner.volume_analyzer import VolumeSetupAnalyzer
from src.scanner.data_fetcher import fetch_historical_data   # use your existing
from src.telegram.poster import send_message                 # your poster function

class MasterScanner:
    def __init__(self):
        self.analyzer = VolumeSetupAnalyzer(volume_period=15, sma_period=15)
        self.cache_file = "data/last_scanner_cache.json"

    # ---------- 1. Morning Pre-Market Gap ----------
    def scan_premarket_gap(self):
        df = fetch_historical_data("NIFTY", interval="daily", days=20)
        if df is None or df.empty:
            return
        setups = self.analyzer.detect_setups(df)
        if not setups:
            msg = "🌅 Pre-Market: No significant volume setup detected."
            send_message("free_main", msg)
            return
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

    # ---------- 2. Pre-Open Top/Bottom Stocks ----------
    def scan_preopen_top_bottom(self):
        # Replace with actual pre-open list from Zerodha if available
        top_bottom_list = self._get_preopen_list()
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
            msg = "📊 *Pre-Open Stock Patterns*\n" + "\n".join(results) + "\n⚠️ Educational."
        else:
            msg = "📊 Pre-Open: No qualifying volume setups."
        send_message("free_main", msg)

    # ---------- 3. Intraday F&O (real-time to premium) ----------
    def scan_intraday_fno(self):
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
                       f"📏 Range: {latest['range']}\n⚠️ Educational.")
                send_message("premium", msg)   # real-time to premium channel
                alerts.append({"symbol": symbol, "setup": latest, "price": current})
        self._cache_alerts(alerts)
        self.analyzer.min_candles = 5

    # ---------- 4. Multibagger (Daily) ----------
    def scan_multibagger(self, asset_list, name="Multibagger"):
        self.analyzer.min_candles = 6
        results = []
        for symbol in asset_list[:100]:
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
            msg = f"📈 *{name} Candidates (Weekly/Monthly)*\n" + "\n".join(results[:10]) + "\n⚠️ Educational."
            send_message("premium_elite", msg)
        self.analyzer.min_candles = 5

    # ---------- 5. Currency ----------
    def scan_currency(self):
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
            send_message("premium", msg)

    # ---------- 6. Commodity ----------
    def scan_commodity(self):
        commodities = ["GOLD", "SILVER", "CRUDEOIL", "NATURALGAS"]
        for comm in commodities:
            msg = f"🛢️ *Commodity Observation* – {comm}\n"
            df_intra = fetch_historical_data(comm, interval="3minute", days=2)
            if df_intra is not None and not df_intra.empty:
                setups = self.analyzer.detect_setups(df_intra)
                if setups:
                    s = setups[-1]
                    msg += f"📊 Intraday range: {s['bottom']} – {s['top']}\n"
            df_daily = fetch_historical_data(comm, interval="daily", days=30)
            if df_daily is not None and not df_daily.empty:
                setups = self.analyzer.detect_setups(df_daily)
                if setups:
                    s = setups[-1]
                    msg += f"📈 Daily statistical zone: {s['fab_50']}\n"
            if "Intraday range" in msg or "statistical zone" in msg:
                msg += "⚠️ Educational only."
                send_message("premium", msg)

    # ---------- Helper methods (customize for your data sources) ----------
    def _get_global_sentiment(self):
        # Implement using yfinance or API
        return "Mixed (use live data)"

    def _get_current_futures_price(self):
        # Use zerodha_fetcher if available, else return placeholder
        return 24500

    def _get_preopen_list(self):
        # Replace with actual pre-open gainers/losers from Zerodha
        return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    def _get_fno_list(self):
        try:
            df = pd.read_csv("fno_stocks.csv")
            return df['symbol'].tolist()
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
