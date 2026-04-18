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
    def _load_all_instruments(self):
        """Load instruments for NSE, CDS, MCX, NFO (F&O)."""
        exchanges = ["NSE", "CDS", "MCX", "NFO"]
        for exchange in exchanges:
            cache_file = os.path.join(self.cache_dir, f"instruments_{exchange}.csv")
            try:
                # Refresh cache if older than today
                if os.path.exists(cache_file):
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

    # -------------------------------
    # 🔍 TOKEN FETCH (with exchange prefix support)
    # -------------------------------
    def get_instrument_token(self, symbol: str) -> Optional[str]:
        """
        Accepts symbols like:
          - "NSE:RELIANCE"
          - "CDS:USDINR"
          - "MCX:GOLD"
          - "NFO:NIFTY25APRFUT" (if needed)
        Also handles plain symbols (e.g., "RELIANCE") by assuming NSE.
        Special handling for indices: "NIFTY" -> "NIFTY 50", "BANKNIFTY" -> "BANK NIFTY"
        """
        # Parse exchange prefix if present
        if ":" in symbol:
            exchange, tradingsymbol = symbol.split(":", 1)
            exchange = exchange.upper()
        else:
            # Default to NSE for equities, but handle index names
            exchange = "NSE"
            tradingsymbol = symbol

        # Special mapping for indices
        if tradingsymbol.upper() == "NIFTY":
            tradingsymbol = "NIFTY 50"
        elif tradingsymbol.upper() == "BANKNIFTY":
            tradingsymbol = "BANK NIFTY"

        # Get cache for this exchange
        df = self.instrument_cache.get(exchange)
        if df is None:
            logger.warning(f"⚠ No instrument cache for {exchange}")
            return None

        # Try exact match on tradingsymbol
        match = df[df["tradingsymbol"] == tradingsymbol]
        if match.empty:
            # Try case-insensitive partial match (for safety)
            match = df[df["tradingsymbol"].str.upper() == tradingsymbol.upper()]
        if match.empty:
            logger.warning(f"⚠ Token not found for {symbol} (exchange={exchange}, tradingsymbol={tradingsymbol})")
            return None

        return str(match.iloc[0]["instrument_token"])

    # -------------------------------
    # 📊 MAIN DATA FUNCTION
    # -------------------------------
    def get_stock_data(self, symbol: str, interval: str = "day", days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for any instrument.
        interval: 'day', '3minute', '30minute' (Kite accepts these)
        """
        if not self.kite:
            return None

        # Fix common interval name
        if interval == "daily":
            interval = "day"

        try:
            token = self.get_instrument_token(symbol)
            if not token:
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
                return None

            df = pd.DataFrame(candles)
            # Rename to lowercase for consistency with rest of system
            df.rename(columns={
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }, inplace=True)
            # Ensure datetime index
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
        """Wrapper to match the name used in data_fetcher.py"""
        return self.get_stock_data(symbol, interval, days)


# Optional: create a singleton instance for easy import
_instance = None
def get_zerodha_fetcher():
    global _instance
    if _instance is None:
        _instance = ZerodhaFetcher()
    return _instance
