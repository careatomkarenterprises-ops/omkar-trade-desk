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
        os.makedirs("data", exist_ok=True)

    def _safe_fetch(self, symbol, interval, days=5):
        try:
            return fetch_historical_data(symbol, interval, days)
        except Exception as e:
            logger.error(f"Fetch error {symbol}: {e}")
            return None

    # ---------- Helper: Nifty & Bank Nifty futures ----------
    def _get_future_symbols(self):
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day
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
        curr_m = month_names[curr_month-1]
        next_m = month_names[next_month-1]
        yr_suffix = str(curr_year)[-2:]
        next_yr = str(next_year)[-2:]
        nifty_curr = f"NFO:NIFTY{yr_suffix}{curr_m}FUT"
        nifty_next = f"NFO:NIFTY{next_yr}{next_m}FUT"
        bn_curr = f"NFO:BANKNIFTY{yr_suffix}{curr_m}FUT"
        bn_next = f"NFO:BANKNIFTY{next_yr}{next_m}FUT"
        return [nifty_curr, nifty_next, bn_curr, bn_next]

    # ---------- Helper: Commodity futures ----------
    def _get_commodity_futures(self):
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day
        if day > 20:
            curr_month = month + 1
            curr_year = year
            if curr_month > 12:
                curr_month = 1
                curr_year += 1
        else:
            curr_month = month
            curr_year = year
        month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                       "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        month_suffix = month_names[curr_month-1]
        year_suffix = str(curr_year)[-2:]
        gold = f"MCX:GOLD{year_suffix}{month_suffix}FUT"
        silver = f"MCX:SILVER{year_suffix}{month_suffix}FUT"
        crude = f"MCX:CRUDEOIL{year_suffix}{month_suffix}FUT"
        natgas = f"MCX:NATGAS{year_suffix}{month_suffix}FUT"
        return [gold, silver, crude, natgas]

    # ---------- NEW: NSE Official Pre-Open Top/Bottom Stocks ----------
    def scan_nse_preopen_top_bottom(self):
        """Fetch official NSE pre-open top gainers and losers"""
        try:
            # NSE pre-open API endpoint
            url = "https://www.nseindia.com/api/market-data-pre-open"
            
            # Headers to mimic a browser (NSE requires these)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.nseindia.com/"
            }
            
            # First request to get cookies (NSE requires this)
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers)
            
            # Second request to get pre-open data
            response = session.get(url, headers=headers)
            data = response.json()
            
            if not data or 'data' not in data:
                send_message("free_main", "📊 Pre-Open: Unable to fetch NSE pre-open data.")
                return
            
            # Parse top gainers (highest percentage change)
            stocks = data['data']
            # Sort by percentage change (highest first)
            stocks_sorted = sorted(stocks, key=lambda x: float(x.get('pChange', 0)), reverse=True)
            
            top_gainers = stocks_sorted[:10]
            top_losers = stocks_sorted[-10:][::-1]  # Reverse to show most negative first
            
            # Build message
            msg = "📊 *NSE Pre-Open Market (Official)*\n\n"
            
            msg += "🟢 *Top Gainers:*\n"
            for stock in top_gainers:
                symbol = stock.get('symbol', 'N/A')
                pChange = stock.get('pChange', 0)
                lastPrice = stock.get('lastPrice', 0)
                msg += f"• {symbol}: ↑ {pChange}% (₹{lastPrice})\n"
            
            msg += "\n🔴 *Top Losers:*\n"
            for stock in top_losers:
                symbol = stock.get('symbol', 'N/A')
                pChange = stock.get('pChange', 0)
                lastPrice = stock.get('lastPrice', 0)
                msg += f"• {symbol}: ↓ {abs(pChange)}% (₹{lastPrice})\n"
            
            msg += "\n⚠️ Educational purpose only."
            send_message("free_main", msg)
            
            # Now run volume setup analysis on these stocks
            self._analyze_preopen_stocks(top_gainers + top_losers)
            
        except Exception as e:
            logger.error(f"NSE pre-open fetch error: {e}")
            send_message("free_main", "📊 Pre-Open: Unable to fetch NSE data. Market may not be open.")

    def _analyze_preopen_stocks(self, stocks):
        """Run volume setup analysis on pre-open stocks using 30-min chart"""
        results = []
        for stock in stocks[:20]:  # Top 20 from gainers+losers
            symbol = stock.get('symbol')
            if not symbol:
                continue
            
            # Fetch 30-min chart data for volume setup analysis
            df = self._safe_fetch(f"NSE:{symbol}", "30minute", 5)
            if df is None:
                continue
            
            setups = self.analyzer.detect_setups(df)
            if not setups:
                continue
            
            latest = setups[-1]
            current = df['close'].iloc[-1]
            
            if current > latest['top']:
                signal = "🔴 Above resistance"
            elif current < latest['bottom']:
                signal = "🟢 Below support"
            else:
                signal = "⚪ Inside range"
            
            results.append(f"• {symbol}: {signal} | Range: {latest['bottom']}-{latest['top']} | Statistical zone: {latest['fab_50']}")
        
        if results:
            msg = "📊 *Volume Setup Analysis (Pre-Open Stocks)*\n" + "\n".join(results[:10]) + "\n⚠️ Educational."
            send_message("free_main", msg)

    # ---------- 1. Morning Pre-Market Gap ----------
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
                global_sentiment = "Neutral"
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

    # ---------- 2. Pre-Open Top/Bottom Stocks (F&O List) ----------
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
                    change_percent = ((pre_open_price - prev_close) / prev_close) * 100
                    results.append(f"• {symbol}: ↑ {change_percent:.2f}% (pre-open: {pre_open_price:.2f})")
                elif pre_open_price < prev_close:
                    change_percent = ((prev_close - pre_open_price) / prev_close) * 100
                    results.append(f"• {symbol}: ↓ {change_percent:.2f}% (pre-open: {pre_open_price:.2f})")
            
            if results:
                msg = "📊 *F&O Pre-Open Movement*\n" + "\n".join(results[:10]) + "\n⚠️ Educational."
            else:
                msg = "📊 Pre-Open: No significant pre-market movement in F&O stocks."
            send_message("free_main", msg)
        except Exception as e:
            logger.error(f"Pre-open F&O error: {e}")

    # ---------- 3. Intraday F&O + Index Futures ----------
    def scan_intraday_fno(self):
        try:
            future_symbols = self._get_future_symbols()
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

    # ---------- 4. Multibagger ----------
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

    # ---------- 5. Currency (Zerodha CDS Exchange) ----------
    def scan_currency(self):
        try:
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

    # ---------- 6. Commodity ----------
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
    scanner.scan_nse_preopen_top_bottom()  # NEW: Official NSE pre-open data
    scanner.scan_preopen_top_bottom_fno()   # F&O pre-open movement
    scanner.scan_intraday_fno()
    scanner.scan_multibagger(scanner._get_fno_list(), "F&O Multibagger")
    scanner.scan_currency()
    scanner.scan_commodity()
    logger.info("All scanners executed successfully")
