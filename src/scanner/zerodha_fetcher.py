import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY")
        self.access_token = os.getenv("KITE_ACCESS_TOKEN")

        if not self.api_key or not self.access_token:
            logger.error("❌ Missing KITE API credentials in environment")
            self.kite = None
            return

        try:
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            # Basic connectivity test
            self.kite.profile()
            logger.info("✅ Zerodha Connection Successful")
        except Exception as e:
            logger.error(f"❌ Zerodha Connection Failed: {e}")
            self.kite = None

        self.cache_file = "data/zerodha_instruments.csv"
        os.makedirs("data", exist_ok=True)
        self.load_instruments()

    def load_instruments(self):
        if not self.kite: return
        try:
            if os.path.exists(self.cache_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
                if mod_time.date() == datetime.now().date():
                    return
            instruments = self.kite.instruments("NSE")
            pd.DataFrame(instruments).to_csv(self.cache_file, index=False)
            logger.info("✅ Instruments cache updated")
        except Exception as e:
            logger.error(f"Error loading instruments: {e}")

    def get_instrument_token(self, symbol: str) -> Optional[str]:
        try:
            df = pd.read_csv(self.cache_file)
            match = df[df["tradingsymbol"] == symbol]
            if not match.empty:
                return str(match.iloc[0]["instrument_token"])
            return None
        except:
            return None

    def get_stock_data(self, symbol: str, interval: str = "day", days: int = 30) -> Optional[pd.DataFrame]:
        if not self.kite: return None
        try:
            token = self.get_instrument_token(symbol)
            if not token: return None
            
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            candles = self.kite.historical_data(
                int(token), 
                from_date.strftime("%Y-%m-%d"), 
                to_date.strftime("%Y-%m-%d"), 
                interval
            )
            if candles:
                df = pd.DataFrame(candles)
                # Ensure lowercase columns for compatibility
                df.columns = [c.lower() for c in df.columns]
                return df
            return None
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
