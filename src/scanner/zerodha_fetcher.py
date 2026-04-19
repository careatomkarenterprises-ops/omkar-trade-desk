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
        self._token_valid = False

        if not self.api_key or not self.access_token:
            logger.error("❌ Missing KITE_API_KEY or KITE_ACCESS_TOKEN in secrets")
            return

        try:
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            # Test token validity by fetching user profile
            profile = self.kite.profile()
            if profile:
                self._token_valid = True
                logger.info(f"✅ Zerodha Connection Successful (User: {profile.get('user_name', 'Unknown')})")
            else:
                logger.error("❌ Zerodha token validation failed")
        except Exception as e:
            logger.error(f"❌ Zerodha Connection Failed: {e}")
            logger.error("   → Your KITE_ACCESS_TOKEN may be expired or invalid.")
            logger.error("   → Generate a new token at https://kite.trade/dashboard")

        self.cache_dir = "data"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.instrument_cache = {}
        self._load_all_instruments()

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

    def get_instrument_token(self, symbol: str) -> Optional[str]:
        if ":" in symbol:
            exchange, tradingsymbol = symbol.split(":", 1)
            exchange = exchange.upper()
        else:
            exchange = "NSE"
            tradingsymbol = symbol

        if tradingsymbol.upper() == "NIFTY":
            tradingsymbol = "NIFTY 50"

        df = self.instrument_cache.get(exchange)
        if df is None or df.empty:
            self._load_all_instruments(force_refresh=True)
            df = self.instrument_cache.get(exchange)

        if df is None or df.empty:
            return None

        match = df[df["tradingsymbol"] == tradingsymbol]
        if not match.empty:
            return str(match.iloc[0]["instrument_token"])

        if exchange == "MCX":
            import re
            underlying_match = re.match(r"([A-Z]+)\d+", tradingsymbol)
            if underlying_match:
                underlying = underlying_match.group(1)
                futures = df[df["tradingsymbol"].str.contains(f"^{underlying}\\d+.*FUT$", regex=True)]
                if not futures.empty:
                    futures = futures.sort_values("tradingsymbol")
                    token = str(futures.iloc[0]["instrument_token"])
                    selected = futures.iloc[0]["tradingsymbol"]
                    logger.info(f"✅ Using nearest {underlying} futures: {selected}")
                    return token

        return None

    def get_stock_data(self, symbol: str, interval: str = "day", days: int = 30) -> Optional[pd.DataFrame]:
        if not self.kite or not self._token_valid:
            logger.error(f"Cannot fetch {symbol}: Zerodha token invalid or missing")
            return None

        if interval == "daily":
            interval = "day"

        try:
            token = self.get_instrument_token(symbol)
            if not token:
                logger.warning(f"⚠ No token for {symbol}")
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
            error_msg = str(e)
            if "Incorrect `api_key` or `access_token`" in error_msg:
                logger.error(f"❌ Zerodha token error for {symbol}: {error_msg}")
                logger.error("   → Please regenerate your KITE_ACCESS_TOKEN at https://kite.trade/dashboard")
                logger.error("   → Then update the KITE_ACCESS_TOKEN secret in GitHub")
            else:
                logger.error(f"Error fetching {symbol}: {e}")
            return None

    def get_historical_data(self, symbol: str, interval: str = "day", days: int = 30):
        return self.get_stock_data(symbol, interval, days)


_instance = None
def get_zerodha_fetcher():
    global _instance
    if _instance is None:
        _instance = ZerodhaFetcher()
    return _instance