import pandas as pd
from src.scanner.volume_analyzer import VolumeSetupAnalyzer
from src.scanner.data_fetcher import fetch_historical_data, get_preopen_top_bottom
from src.telegram.poster import send_alert, send_delayed_alert

class MasterScanner:
    def __init__(self):
        self.analyzer = VolumeSetupAnalyzer(volume_period=15, sma_period=15)

    # ---------- 1. Morning Pre-Market Gap ----------
    def scan_premarket_gap(self):
        df = fetch_historical_data("NIFTY", interval="daily", days=20)
        setups = self.analyzer.detect_setups(df)
        if not setups:
            return "Neutral – no volume setup"
        latest = setups[-1]
        global_sentiment = self.get_global_sentiment()  # SGX Nifty, Dow Futures
        bias = "Up" if self.get_current_futures_price() > latest['top'] else "Down"
        msg = (f"🌅 Pre‑Market Observation\n"
               f"📊 Setup: {latest['candles']} high‑volume candles\n"
               f"📐 Observed range: {latest['bottom']} – {latest['top']}\n"
               f"🎯 Statistical zone: {latest['fab_50']}\n"
               f"🌍 Global cues: {global_sentiment}\n"
               f"📈 Bias: {bias}\n⚠️ Educational only.")
        send_alert(msg, "@OmkarFree")
        return bias

    # ---------- 2. Pre-Open Top/Bottom Stocks (30-min chart) ----------
    def scan_preopen_top_bottom(self):
        top_bottom_list = get_preopen_top_bottom()  # from Zerodha pre-market
        results = []
        for symbol in top_bottom_list[:20]:  # limit to top 20
            df = fetch_historical_data(symbol, interval="30minute", days=5)
            setups = self.analyzer.detect_setups(df)
            if not setups:
                continue
            latest = setups[-1]
            current = df['close'].iloc[-1]
            side = "Above resistance" if current > latest['top'] else ("Below support" if current < latest['bottom'] else "Inside range")
            results.append(f"• {symbol}: {side}, range {latest['bottom']}-{latest['top']}")
        msg = "📊 *Pre‑Open Stock Patterns*\n" + "\n".join(results) + "\n⚠️ Educational only."
        send_alert(msg, "@OmkarFree")
        return results

    # ---------- 3. After-Open F&O + Index (3-min, min_candles=6) ----------
    def scan_intraday_fno(self, channel="@OmkarPro"):
        symbols = pd.read_csv("fno_stocks.csv")['symbol'].tolist() + ["NIFTY", "BANKNIFTY"]
        for symbol in symbols:
            df = fetch_historical_data(symbol, interval="3minute", days=2)
            self.analyzer.min_candles = 6  # override for this scan
            setups = self.analyzer.detect_setups(df)
            if not setups:
                continue
            latest = setups[-1]
            current = df['close'].iloc[-1]
            sma_cross = self.analyzer.check_sma_crossover(df)
            if current > latest['top'] and sma_cross:
                msg = (f"📊 *Intraday Pattern* – {symbol}\n"
                       f"📈 Setup: {latest['candles']} candles\n"
                       f"🔴 Upper bound: {latest['top']}\n"
                       f"🟢 Lower bound: {latest['bottom']}\n"
                       f"🎯 Statistical zone: {latest['fab_50']}\n"
                       f"⚠️ Educational observation.")
                send_alert(msg, channel)   # premium gets real-time
                # Also cache for delayed free post
                self.cache_for_free(symbol, latest, current)
        self.analyzer.min_candles = 5  # reset

    # ---------- 4 & 5. Multibagger (Daily, min_candles=6, breakout with low volume) ----------
    def scan_multibagger(self, asset_list, name="Multibagger"):
        self.analyzer.min_candles = 6
        results = []
        for symbol in asset_list:
            df = fetch_historical_data(symbol, interval="daily", days=60)
            setups = self.analyzer.detect_setups(df)
            if not setups:
                continue
            latest = setups[-1]
            # Check breakout closing above resistance with below‑average volume
            last_close = df['close'].iloc[-1]
            last_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(15).mean().iloc[-1]
            if last_close > latest['top'] and last_volume < avg_volume:
                results.append(f"• {symbol}: breakout above {latest['top']} on low volume – watch for continuation.")
        msg = "📈 *Multibagger Candidates (Weekly/Monthly)*\n" + "\n".join(results[:10]) + "\n⚠️ Educational."
        send_alert(msg, "@OmkarProElite")  # premium elite channel
        self.analyzer.min_candles = 5
        return results

    # ---------- 6. News (already exists, just segregate) ----------
    # Use existing news aggregator – free gets headlines, premium gets detailed impact.

    # ---------- 7. Currency (3-min, min_candles=5) ----------
    def scan_currency(self):
        pairs = ["USDINR", "EURINR", "GBPINR", "JPYINR"]
        for pair in pairs:
            df = fetch_historical_data(pair, interval="3minute", days=2)
            setups = self.analyzer.detect_setups(df)
            if not setups:
                continue
            latest = setups[-1]
            current = df['close'].iloc[-1]
            bias = "upward" if current > latest['top'] else ("downward" if current < latest['bottom'] else "sideways")
            msg = (f"💱 *Currency Pattern* – {pair}\n"
                   f"📊 Setup: {latest['candles']} candles\n"
                   f"📐 Range: {latest['bottom']} – {latest['top']}\n"
                   f"📈 Bias: {bias}\n⚠️ Educational.")
            send_alert(msg, "@OmkarPro")  # premium channel
        return

    # ---------- 8. Commodity (3-min + Daily) ----------
    def scan_commodity(self):
        commodities = ["GOLD", "SILVER", "CRUDEOIL", "NATURALGAS"]
        for comm in commodities:
            # Intraday 3-min
            df_intra = fetch_historical_data(comm, interval="3minute", days=2)
            setups_intra = self.analyzer.detect_setups(df_intra)
            # Daily positional
            df_daily = fetch_historical_data(comm, interval="daily", days=30)
            setups_daily = self.analyzer.detect_setups(df_daily)
            msg = f"🛢️ *Commodity Observation* – {comm}\n"
            if setups_intra:
                s = setups_intra[-1]
                msg += f"📊 Intraday range: {s['bottom']} – {s['top']}\n"
            if setups_daily:
                s = setups_daily[-1]
                msg += f"📈 Daily statistical zone: {s['fab_50']}\n"
            msg += "⚠️ Educational only."
            send_alert(msg, "@OmkarPro")
        return

    # Helper methods
    def get_global_sentiment(self):
        # fetch SGX Nifty, Dow Futures, Asian markets
        return "Positive"  # mock

    def get_current_futures_price(self):
        return 24500  # mock – use Zerodha API

    def cache_for_free(self, symbol, setup, price):
        # store in JSON for delayed posting (30 min later)
        pass

# Entry point for GitHub Actions
if __name__ == "__main__":
    scanner = MasterScanner()
    scanner.scan_premarket_gap()
    scanner.scan_preopen_top_bottom()
    scanner.scan_intraday_fno()          # real-time to premium
    scanner.scan_multibagger(pd.read_csv("fno_stocks.csv")['symbol'], "F&O Multibagger")
    scanner.scan_multibagger(pd.read_csv("nse_all_stocks.csv")['symbol'], "All Stocks Multibagger")
    scanner.scan_currency()
    scanner.scan_commodity()
