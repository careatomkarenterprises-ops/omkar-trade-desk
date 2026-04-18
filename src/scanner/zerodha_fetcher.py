import os
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ZerodhaFetcher:
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY")
        self.access_token = os.getenv("KITE_ACCESS_TOKEN")
        self.kite = None

        if not self.api_key or not self.access_token:
            logger.error("❌ Missing KITE API credentials")
            return

        try:
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            logger.info("✅ Zerodha Connection Successful")
        except Exception as e:
            logger.error(f"❌ Zerodha Connection Failed: {e}")

        self.cache_dir = "data"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.instrument_cache = {}  # exchange -> DataFrame
        self._load_all_instruments()

    # -------------------------------
    # 📦 LOAD INSTRUMENTS FOR ALL EXCHANGES (with force refresh)
    # -------------------------------
    def _load_all_instruments(self, force_refresh=False):
        exchanges = ["NSE", "CDS", "MCX", "NFO"]
        for exchange in exchanges:
            cache_file = os.path.join(self.cache_dir, f"instruments_{exchange}.csv")
            try:
                if not force_refresh and os.path.exists(cache_file):
                    mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                    if mod_time.date() == datetime.now().date():
                        df = pd.read_csv(cache_file)
                        self.instrument_cache[exchange] = df
                        continue

                if not self.kite:
                    continue
                instruments = self.kite.instruments(exchange)
                df = pd.DataFrame(instruments)
                df.to_csv(cache_file, index=False)
                self.instrument_cache[exchange] = df
                logger.info(f"✅ Loaded {len(df)} instruments for {exchange}")
            except Exception as e:
                logger.error(f"Error loading {exchange} instruments: {e}")
                self.instrument_cache[exchange] = pd.DataFrame()  # empty fallback

    # -------------------------------
    # 🔍 TOKEN FETCH with fallback and debug logging
    # -------------------------------
    def get_instrument_token(self, symbol: str) -> Optional[str]:
        # Parse exchange and tradingsymbol
        if ":" in symbol:
            exchange, tradingsymbol = symbol.split(":", 1)
            exchange = exchange.upper()
        else:
            exchange = "NSE"
            tradingsymbol = symbol

        # Special mappings
        if tradingsymbol.upper() == "NIFTY":
            tradingsymbol = "NIFTY 50"
        # BANKNIFTY stays as is (no space)

        df = self.instrument_cache.get(exchange)
        if df is None or df.empty:
            # Try to reload instruments for this exchange
            self._load_all_instruments(force_refresh=True)
            df = self.instrument_cache.get(exchange)

        if df is None or df.empty:
            logger.warning(f"⚠ No instrument data for {exchange} – cannot find token for {symbol}")
            return None

        # Try exact match
        match = df[df["tradingsymbol"] == tradingsymbol]
        if match.empty:
            # Try case‑insensitive
            match = df[df["tradingsymbol"].str.upper() == tradingsymbol.upper()]
        if match.empty:
            # Log some sample symbols for debugging (first 20)
            sample = df['tradingsymbol'].head(20).tolist()
            logger.warning(f"⚠ Token not found for {symbol} (exchange={exchange}, tradingsymbol={tradingsymbol})")
            logger.warning(f"   Sample symbols on {exchange}: {sample}")
            # Try alternate exchange for BANKNIFTY (maybe it's on NFO)
            if tradingsymbol.upper() == "BANKNIFTY" and exchange == "NSE":
                logger.info("   Retrying with NFO exchange...")
                return self.get_instrument_token(f"NFO:BANKNIFTY")
            return None

        return str(match.iloc[0]["instrument_token"])

    # -------------------------------
    # 📊 MAIN DATA FUNCTION with yfinance fallback
    # -------------------------------
    def get_stock_data(self, symbol: str, interval: str = "day", days: int = 30) -> Optional[pd.DataFrame]:
        if not self.kite:
            return self._fallback_yfinance(symbol, interval, days)

        # Fix interval name
        if interval == "daily":
            interval = "day"

        try:
            token = self.get_instrument_token(symbol)
            if not token:
                logger.warning(f"⚠ No token for {symbol}, falling back to yfinance")
                return self._fallback_yfinance(symbol, interval, days)

            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)

            candles = self.kite.historical_data(
                int(token),
                from_date.strftime("%Y-%m-%d"),
                to_date.strftime("%Y-%m-%d"),
                interval
            )

            if not candles:
                return self._fallback_yfinance(symbol, interval, days)

            df = pd.DataFrame(candles)
            df.rename(columns={
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            return df[['open', 'high', 'low', 'close', 'volume']]

        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return self._fallback_yfinance(symbol, interval, days)

    # -------------------------------
    # 🛡️ FALLBACK to yfinance (works for equities, indices, some currencies)
    # -------------------------------
    def _fallback_yfinance(self, symbol: str, interval: str = "day", days: int = 30) -> Optional[pd.DataFrame]:
        try:
            # Remove exchange prefix for yfinance
            if ":" in symbol:
                clean_symbol = symbol.split(":", 1)[1]
            else:
                clean_symbol = symbol

            # Map interval
            yf_interval = "1d" if interval == "day" else ("5m" if interval == "3minute" else "30m")
            period = f"{days+2}d"
            ticker = yf.Ticker(clean_symbol)
            df = ticker.history(period=period, interval=yf_interval)
            if df.empty:
                return None
            df = df.rename(columns=str.lower)
            df.index.name = 'date'
            required = ['open', 'high', 'low', 'close', 'volume']
            if all(col in df.columns for col in required):
                return df[required]
            return None
        except Exception as e:
            logger.error(f"yfinance fallback error for {symbol}: {e}")
            return None

    # -------------------------------
    # ✅ COMPATIBILITY WRAPPER
    # -------------------------------
    def get_historical_data(self, symbol: str, interval: str = "day", days: int = 30):
        return self.get_stock_data(symbol, interval, days)


_instance = None
def get_zerodha_fetcher():
    global _instance
    if _instance is None:
        _instance = ZerodhaFetcher()
    return _instance
