import os
import logging
import pandas as pd

from datetime import datetime, timedelta
from typing import Optional

from kiteconnect import KiteConnect
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ZerodhaFetcher:

    def __init__(self):

        self.api_key = os.getenv("KITE_API_KEY")
        self.access_token = os.getenv("KITE_ACCESS_TOKEN")

        self.kite = None
        self._token_valid = False

        self.cache_dir = "data"

        os.makedirs(self.cache_dir, exist_ok=True)

        self.instrument_cache = {}

        logger.info("===== INITIALIZING ZERODHA FETCHER =====")

        if not self.api_key:
            logger.error("❌ Missing KITE_API_KEY")
            return

        if not self.access_token:
            logger.error("❌ Missing KITE_ACCESS_TOKEN")
            return

        try:

            self.kite = KiteConnect(api_key=self.api_key)

            self.kite.set_access_token(self.access_token)

            profile = self.kite.profile()

            self._token_valid = True

            logger.info(
                f"✅ Zerodha Connected Successfully | User: {profile.get('user_name')}"
            )

            self._load_all_instruments()

        except Exception as e:

            logger.error(f"❌ Zerodha Connection Failed: {e}")

            logger.error("⚠ Your ACCESS TOKEN may be expired")

            logger.error("⚠ Generate new token daily before market opens")

    # ==========================================================
    # LOAD INSTRUMENTS
    # ==========================================================

    def _load_all_instruments(self, force_refresh=False):

        exchanges = ["NSE", "NFO", "MCX", "CDS"]

        for exchange in exchanges:

            try:

                cache_file = os.path.join(
                    self.cache_dir,
                    f"instruments_{exchange}.csv"
                )

                use_cache = False

                if os.path.exists(cache_file):

                    modified = datetime.fromtimestamp(
                        os.path.getmtime(cache_file)
                    )

                    if modified.date() == datetime.now().date():
                        use_cache = True

                if use_cache and not force_refresh:

                    df = pd.read_csv(cache_file)

                    self.instrument_cache[exchange] = df

                    logger.info(
                        f"✅ Loaded Cached {exchange} Instruments: {len(df)}"
                    )

                    continue

                if not self.kite:
                    continue

                instruments = self.kite.instruments(exchange)

                df = pd.DataFrame(instruments)

                df.to_csv(cache_file, index=False)

                self.instrument_cache[exchange] = df

                logger.info(
                    f"✅ Downloaded {exchange} Instruments: {len(df)}"
                )

            except Exception as e:

                logger.error(
                    f"❌ Error Loading {exchange} Instruments: {e}"
                )

                self.instrument_cache[exchange] = pd.DataFrame()

    # ==========================================================
    # FIND TOKEN
    # ==========================================================

    def get_instrument_token(self, symbol: str) -> Optional[int]:

        try:

            if ":" in symbol:

                exchange, tradingsymbol = symbol.split(":", 1)

                exchange = exchange.upper()

            else:

                exchange = "NSE"

                tradingsymbol = symbol.upper()

            if tradingsymbol == "NIFTY":
                tradingsymbol = "NIFTY 50"

            df = self.instrument_cache.get(exchange)

            if df is None or df.empty:

                self._load_all_instruments(force_refresh=True)

                df = self.instrument_cache.get(exchange)

            if df is None or df.empty:
                return None

            match = df[df["tradingsymbol"] == tradingsymbol]

            if not match.empty:

                return int(match.iloc[0]["instrument_token"])

            # AUTO HANDLE MCX FUTURES

            if exchange == "MCX":

                futures = df[
                    df["tradingsymbol"].str.contains(
                        tradingsymbol,
                        case=False,
                        na=False
                    )
                ]

                if not futures.empty:

                    futures = futures.sort_values("expiry")

                    token = int(futures.iloc[0]["instrument_token"])

                    selected = futures.iloc[0]["tradingsymbol"]

                    logger.info(
                        f"✅ Using MCX Contract: {selected}"
                    )

                    return token

            return None

        except Exception as e:

            logger.error(f"❌ Token Fetch Error: {e}")

            return None

    # ==========================================================
    # HISTORICAL DATA
    # ==========================================================

    def get_stock_data(
        self,
        symbol: str,
        interval: str = "day",
        days: int = 30
    ) -> Optional[pd.DataFrame]:

        if not self.kite or not self._token_valid:

            logger.error(
                f"❌ Zerodha Session Invalid | Cannot Fetch {symbol}"
            )

            return None

        try:

            token = self.get_instrument_token(symbol)

            if not token:

                logger.warning(
                    f"⚠ Instrument Token Not Found: {symbol}"
                )

                return None

            to_date = datetime.now()

            from_date = to_date - timedelta(days=days)

            candles = self.kite.historical_data(
                instrument_token=token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )

            if not candles:

                logger.warning(
                    f"⚠ No Candle Data: {symbol}"
                )

                return None

            df = pd.DataFrame(candles)

            df["date"] = pd.to_datetime(df["date"])

            df.set_index("date", inplace=True)

            columns_needed = [
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]

            df = df[columns_needed]

            logger.info(
                f"✅ Data Loaded: {symbol} | Rows: {len(df)}"
            )

            return df

        except Exception as e:

            logger.error(
                f"❌ Historical Data Error ({symbol}): {e}"
            )

            return None

    # ==========================================================
    # ALIAS
    # ==========================================================

    def get_historical_data(
        self,
        symbol,
        interval="day",
        days=30
    ):

        return self.get_stock_data(
            symbol,
            interval,
            days
        )


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================

_instance = None


def get_zerodha_fetcher():

    global _instance

    if _instance is None:

        _instance = ZerodhaFetcher()

    return _instance
