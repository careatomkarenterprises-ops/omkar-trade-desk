import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from typing import Optional, Dict, List
from dotenv import load_dotenv

# ✅ Load .env from root properly
load_dotenv(dotenv_path=".env")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ZerodhaFetcher:
    def __init__(self):
        # ✅ Read credentials from .env
        self.api_key = os.getenv("KITE_API_KEY")
        self.access_token = os.getenv("KITE_ACCESS_TOKEN")

        # 🔍 Debug check (IMPORTANT)
        logger.info(f"API KEY Loaded: {bool(self.api_key)}")
        logger.info(f"ACCESS TOKEN Loaded: {bool(self.access_token)}")

        if not self.api_key or not self.access_token:
            raise ValueError("❌ Missing KITE API credentials in .env")

        # ✅ Initialize Kite
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)

        # ✅ Validate connection
        try:
            profile = self.kite.profile()
            logger.info(f"✅ Connected to Zerodha as {profile['user_name']}")
        except Exception as e:
            raise ValueError(f"❌ Invalid Access Token or API issue: {e}")

        # 📁 Setup cache
        self.cache_file = "data/zerodha_instruments.csv"
        os.makedirs("data", exist_ok=True)
        self.instrument_cache = {}

        self.load_instruments()

    # ----------------------------------------
    # LOAD INSTRUMENTS
    # ----------------------------------------
    def load_instruments(self):
        try:
            if os.path.exists(self.cache_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
                if mod_time.date() == datetime.now().date():
                    logger.info("✅ Using cached instruments")
                    return

            logger.info("📥 Downloading instruments...")
            instruments = self.kite.instruments()
            pd.DataFrame(instruments).to_csv(self.cache_file, index=False)
            logger.info("✅ Instruments updated")

        except Exception as e:
            logger.error(f"❌ Error loading instruments: {e}")

    # ----------------------------------------
    # GET INSTRUMENT TOKEN
    # ----------------------------------------
    def get_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        try:
            cache_key = f"{exchange}:{symbol}"

            if cache_key in self.instrument_cache:
                return self.instrument_cache[cache_key]

            df = pd.read_csv(self.cache_file)

            match = df[
                (df["exchange"] == exchange) &
                (df["tradingsymbol"] == symbol)
            ]

            if match.empty and exchange == "NSE":
                match = df[
                    (df["exchange"] == exchange) &
                    (df["tradingsymbol"] == f"{symbol}EQ")
                ]

            if not match.empty:
                token = str(match.iloc[0]["instrument_token"])
                self.instrument_cache[cache_key] = token
                return token

            logger.warning(f"⚠️ Token not found for {symbol}")
            return None

        except Exception as e:
            logger.error(f"❌ Token fetch error: {e}")
            return None

    # ----------------------------------------
    # GET LTP
    # ----------------------------------------
    def get_ltp(self, symbols: List[str]) -> Dict:
        try:
            formatted = [f"NSE:{s}" for s in symbols]
            ltp_data = self.kite.ltp(formatted)

            return {
                s: ltp_data[f"NSE:{s}"]["last_price"]
                for s in symbols
                if f"NSE:{s}" in ltp_data
            }

        except Exception as e:
            logger.error(f"❌ LTP fetch error: {e}")
            return {}

    # ----------------------------------------
    # HISTORICAL DATA
    # ----------------------------------------
    def get_historical_data(
        self,
        symbol: str,
        interval: str = "day",
        days: int = 45
    ) -> Optional[pd.DataFrame]:

        try:
            token = self.get_instrument_token(symbol)

            if not token:
                return None

            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)

            candles = self.kite.historical_data(
                int(token),
                from_date.strftime("%Y-%m-%d %H:%M:%S"),
                to_date.strftime("%Y-%m-%d %H:%M:%S"),
                interval
            )

            if candles:
                df = pd.DataFrame(candles)
                df.rename(columns={
                    "date": "Date",
                    "open": "Open",
                    "high": "High",
                    "low": "Low",
                    "close": "Close",
                    "volume": "Volume"
                }, inplace=True)

                df.set_index("Date", inplace=True)
                return df

            return None

        except Exception as e:
            logger.error(f"❌ Historical data error: {e}")
            return None
