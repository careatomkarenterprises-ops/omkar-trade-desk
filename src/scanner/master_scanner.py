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
        self.cache_file = "data/last_scanner_cache.json"
        self.delayed_cache_file = "data/delayed_patterns_cache.json"
        os.makedirs("data", exist_ok=True)

    def _safe_fetch(self, symbol, interval, days=5):
        try:
            return fetch_historical_data(symbol, interval, days)
        except Exception as e:
            logger.error(f"Fetch error {symbol}: {e}")
            return None

    def _send_to_all_premium(self, msg):
        send_message("premium", msg)
        send_message("premium_elite", msg)

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

    def _get_fno_list(self):
        try:
            if os.path.exists("fno_stocks.csv"):
                df = pd.read_csv("fno_stocks.csv")
                if 'symbol' in df.columns:
                    symbols = df['symbol'].dropna().tolist()
                    if symbols:
                        logger.info(f"Loaded {len(symbols)} F&O stocks from CSV")
                        return symbols[:50]
        except Exception as e:
            logger.error(f"Error reading fno_stocks.csv: {e}")
        fallback = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        logger.warning(f"Using fallback F&O list: {fallback}")
        return fallback

    def _get_future_symbols(self):
        today = datetime.now()
        year, month, day = today.year, today.month, today.day
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
        month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        curr_m = month_names[curr_month-1]
        next_m = month_names[next_month-1]
        yr_suffix = str(curr_year)[-2:]
        next_yr = str(next_year)[-2:]
        return [
            f"NFO:NIFTY{yr_suffix}{curr_m}FUT",
            f"NFO:NIFTY{next_yr}{next_m}FUT",
            f"NFO:BANKNIFTY{yr_suffix}{curr_m}FUT",
            f"NFO:BANKNIFTY{next_yr}{next_m}FUT"
        ]

        def _get_commodity_futures(self):
    return ["GOLD", "SILVER", "CRUDE"]
        today = datetime.now()
        year, month, day = today.year, today.month, today.day
        if day > 20:
            curr_month = month + 1
            curr_year = year
            if curr_month > 12:
                curr_month = 1
                curr_year += 1
        else:
            curr_month = month
            curr_year = year
        month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        month_suffix = month_names[curr_month-1]
        year_suffix = str(curr_year)[-2:]
        return [
            f"MCX:GOLD{year_suffix}{month_suffix}FUT",
            f"MCX:SILVER{year_suffix}{month_suffix}FUT",
            f"MCX:CRUDEOIL{year_suffix}{month_suffix}FUT",
            f"MCX:NATGAS{year_suffix}{month_suffix}FUT"
        ]

    def scan_premarket_gap(self):
        try:
            df = self._safe_fetch("NIFTY 50", "day", 20)
            if df is None:
                msg = "🌅 Pre-Market: Unable to fetch NIFTY data."
                self._send_to_all_premium(msg)
                send_message("free_main", msg)
                return
            setups = self.analyzer.detect_setups(df)
            if not setups:
                msg = "🌅 Pre-Market: No significant volume setup detected."
            else:
                latest = setups[-1]
                bias = "Sideways"
                msg = (f"🌅 *Pre-Market Observation*\n"
                       f"📊 Volume setup: {latest['candles']} high-volume candles\n"
                       f"📐 Observed range: {latest['bottom']} – {latest['top']}\n"
                       f"🎯 Statistical zone: {latest['fab_50']}\n"
                       f"📈 {bias}\n⚠️ Educational purpose only.")
            self._send_to_all_premium(msg)
            send_message("free_main", msg)
            logger.info("Pre-market gap scan completed")
        except Exception as e:
            logger.error(f"Pre-market scan error: {e}")

    def scan_nse_preopen_top_bottom(self):
        try:
            url = "https://www.nseindia.com/api/market-data-pre-open"
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Referer": "https://www.nseindia.com/"}
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers)
            response = session.get(url, headers=headers)
            data = response.json()
            if not data or 'data' not in data:
                send_message("free_main", "📊 Pre-Open: NSE data not available (market may not be open).")
                return
            stocks = data['data']
            stocks_sorted = sorted(stocks, key=lambda x: float(x.get('pChange', 0)), reverse=True)
            top_gainers = stocks_sorted[:10]
            top_losers = stocks_sorted[-10:][::-1]
            msg = "📊 *NSE Pre-Open Market (Official)*\n\n🟢 *Top Gainers:*\n"
            for stock in top_gainers:
                msg += f"• {stock.get('symbol')}: ↑ {stock.get('pChange')}% (₹{stock.get('lastPrice')})\n"
            msg += "\n🔴 *Top Losers:*\n"
            for stock in top_losers:
                msg += f"• {stock.get('symbol')}: ↓ {abs(float(stock.get('pChange', 0)))}% (₹{stock.get('lastPrice')})\n"
            msg += "\n⚠️ Educational purpose only."
            self._send_to_all_premium(msg)
            send_message("free_main", msg)
        except Exception as e:
            logger.error(f"NSE pre-open error: {e}")

    def scan_preopen_top_bottom_fno(self):
        try:
            symbols = self._get_fno_list()
            results = []
            for symbol in symbols[:20]:
                df = self._safe_fetch(symbol, "minute", 1)
                if df is None or df.empty:
                    continue
                pre_open_price = df['open'].iloc[-1]
                daily_df = self._safe_fetch(symbol, "day", 2)
                if daily_df is None or len(daily_df) < 2:
                    continue
                prev_close = daily_df['close'].iloc[-2]
                if pre_open_price > prev_close:
                    change = ((pre_open_price - prev_close) / prev_close) * 100
                    results.append(f"• {symbol}: ↑ {change:.2f}%")
                elif pre_open_price < prev_close:
                    change = ((prev_close - pre_open_price) / prev_close) * 100
                    results.append(f"• {symbol}: ↓ {change:.2f}%")
            if results:
                msg = "📊 *F&O Pre-Open Movement*\n" + "\n".join(results[:10]) + "\n⚠️ Educational."
                self._send_to_all_premium(msg)
                send_message("free_main", msg)
        except Exception as e:
            logger.error(f"Pre-open F&O error: {e}")

    def scan_intraday_fno(self):
        try:
            symbols = self._get_fno_list() + self._get_future_symbols()
            self.analyzer.min_candles = 6
            for symbol in symbols:
                df = self._safe_fetch(symbol, "5minute", 2)
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
                    self._send_to_all_premium(msg)
                    self._cache_delayed_pattern(symbol, latest, current)
            self.analyzer.min_candles = 5
        except Exception as e:
            logger.error(f"Intraday error: {e}")

    def scan_multibagger(self):
        try:
            symbols = self._get_fno_list()
            self.analyzer.min_candles = 6
            results = []
            for symbol in symbols[:100]:
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
                msg = "📈 *Multibagger Candidates*\n" + "\n".join(results[:10]) + "\n⚠️ Educational."
                self._send_to_all_premium(msg)
            self.analyzer.min_candles = 5
        except Exception as e:
            logger.error(f"Multibagger error: {e}")

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
                bias = "upward" if current > latest['top'] else ("downward" if current < latest['bottom'] else "sideways")
                msg = (f"💱 *Currency Pattern* – {pair}\n"
                       f"📊 Setup: {latest['candles']} candles\n"
                       f"📐 Range: {latest['bottom']} – {latest['top']}\n"
                       f"📈 {bias} bias\n⚠️ Educational.")
                self._send_to_all_premium(msg)
                self._cache_delayed_pattern(pair, latest, current)
        except Exception as e:
            logger.error(f"Currency error: {e}")

    def scan_commodity(self):
        try:
            commodities = self._get_commodity_futures()
            for comm in commodities:
                msg = f"🛢️ *Commodity* – {comm}\n"
                df_intra = self._safe_fetch(comm, "3minute", 2)
                if df_intra is not None:
                    setups = self.analyzer.detect_setups(df_intra)
                    if setups:
                        s = setups[-1]
                        msg += f"📊 Intraday range: {s['bottom']} – {s['top']}\n"
                        self._cache_delayed_pattern(comm, s, df_intra['close'].iloc[-1])
                df_daily = self._safe_fetch(comm, "day", 30)
                if df_daily is not None:
                    setups = self.analyzer.detect_setups(df_daily)
                    if setups:
                        s = setups[-1]
                        msg += f"📈 Daily statistical zone: {s['fab_50']}\n"
                if "Intraday range" in msg or "statistical zone" in msg:
                    msg += "⚠️ Educational."
                    self._send_to_all_premium(msg)
        except Exception as e:
            logger.error(f"Commodity error: {e}")

    def post_delayed_patterns(self):
        try:
            if not os.path.exists(self.delayed_cache_file):
                return
            with open(self.delayed_cache_file, 'r') as f:
                cache = json.load(f)
            if not cache:
                return
            for item in cache:
                symbol = item['symbol']
                setup = item['setup']
                msg = (f"📊 *Delayed Pattern (30 min ago)* – {symbol}\n"
                       f"📈 Setup: {setup['candles']} high-volume candles\n"
                       f"🔴 Upper bound: {setup['top']}\n"
                       f"🟢 Lower bound: {setup['bottom']}\n"
                       f"🎯 Statistical zone: {setup['fab_50']}\n"
                       f"⚠️ Educational - Not a recommendation.\n\n"
                       f"⚡ *Get real-time alerts:* Join @Omkar_Pro")
                send_message("free_signals", msg)
            with open(self.delayed_cache_file, 'w') as f:
                json.dump([], f)
        except Exception as e:
            logger.error(f"Delayed posting error: {e}")

if __name__ == "__main__":
    scanner = MasterScanner()
    scanner.scan_premarket_gap()
    scanner.scan_nse_preopen_top_bottom()
    scanner.scan_preopen_top_bottom_fno()
    scanner.scan_intraday_fno()
    scanner.scan_multibagger()
    scanner.scan_currency()
    scanner.scan_commodity()
    scanner.post_delayed_patterns()
    logger.info("All scanners executed successfully")
