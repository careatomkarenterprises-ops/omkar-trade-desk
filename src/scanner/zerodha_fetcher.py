import os
import logging
import pandas as pd
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
    # 📦 LOAD INSTRUMENTS FOR ALL EXCHANGES
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
                self.instrument_cache[exchange] = pd.DataFrame()

    # -------------------------------
    # 🔍 TOKEN FETCH with dynamic contract search for commodities
    # -------------------------------
    def get_instrument_token(self, symbol: str) -> Optional[str]:
        # Parse exchange and tradingsymbol
        if ":" in symbol:
            exchange, tradingsymbol = symbol.split(":", 1)
            exchange = exchange.upper()
        else:
            exchange = "NSE"
            tradingsymbol = symbol

        # Special mapping for indices
        if tradingsymbol.upper() == "NIFTY":
            tradingsymbol = "NIFTY 50"

        # Get cache for this exchange
        df = self.instrument_cache.get(exchange)
        if df is None or df.empty:
            self._load_all_instruments(force_refresh=True)
            df = self.instrument_cache.get(exchange)

        if df is None or df.empty:
            logger.warning(f"⚠ No instrument data for {exchange}")
            return None

        # First try exact match
        match = df[df["tradingsymbol"] == tradingsymbol]
        if not match.empty:
            return str(match.iloc[0]["instrument_token"])

        # For MCX commodities, try to find the nearest expiry futures contract
        if exchange == "MCX":
            # Extract underlying from symbol (e.g., "GOLD26APRFUT" -> "GOLD")
            import re
            underlying_match = re.match(r"([A-Z]+)\d+", tradingsymbol)
            if underlying_match:
                underlying = underlying_match.group(1)
                # Find all futures contracts for this underlying
                futures = df[df["tradingsymbol"].str.contains(f"^{underlying}\\d+.*FUT$", regex=True)]
                if not futures.empty:
                    # Sort by expiry date (assuming expiry is in the symbol or we have expiry column)
                    # For simplicity, pick the first one (nearest expiry if sorted by instrument_token or name)
                    # Better: sort by tradingsymbol (which contains year+month) lexicographically
                    futures = futures.sort_values("tradingsymbol")
                    selected = futures.iloc[0]["tradingsymbol"]
                    token = str(futures.iloc[0]["instrument_token"])
                    logger.info(f"✅ Using nearest {underlying} futures: {selected}")
                    return token

        # If still not found, log sample symbols for debugging
        sample = df['tradingsymbol'].head(20).tolist()
        logger.warning(f"⚠ Token not found for {symbol} (exchange={exchange}, tradingsymbol={tradingsymbol})")
        logger.warning(f"   Sample symbols on {exchange}: {sample}")
        return None

    # -------------------------------
    # 📊 MAIN DATA FUNCTION (no yFinance fallback)
    # -------------------------------
    def get_stock_data(self, symbol: str, interval: str = "day", days: int = 30) -> Optional[pd.DataFrame]:
        if not self.kite:
            logger.error("Kite instance not available")
            return None

        # Fix interval name
        if interval == "daily":
            interval = "day"

        try:
            token = self.get_instrument_token(symbol)
            if not token:
                logger.warning(f"⚠ No token for {symbol} – skipping (Zerodha only, no fallback)")
                return None

            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)

            candles = self.kite.historical_data(
                int(token),
                from_date.strftime("%Y-%m-%d"),
                to_date.strftime("%Y-%m-%d"),
                interval
            )

            if not candles:
                logger.warning(f"No historical data for {symbol}")
                return None

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