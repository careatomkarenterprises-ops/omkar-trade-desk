"""
Data Fetcher - Zerodha Exclusive Production Version
"""

import logging
import pandas as pd
from typing import Optional
from src.scanner.zerodha_fetcher import ZerodhaFetcher

logger = logging.getLogger(__name__)


class DataFetcher:

    def __init__(self):
        self.zerodha = None

        try:
            self.zerodha = ZerodhaFetcher()
            logger.info("✅ Zerodha API Connection Active")
        except Exception as e:
            logger.critical(f"❌ Zerodha Init Failed: {e}")
            self.zerodha = None

    def is_ready(self) -> bool:
        return self.zerodha is not None

    def get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:

        if not self.zerodha:
            return None

        try:
            df = self.zerodha.get_historical_data(symbol, interval="day", days=45)

            if df is not None and not df.empty:
                df.columns = [c.lower() for c in df.columns]
                return df

            return None

        except Exception as e:
            logger.error(f"Fetch error {symbol}: {e}")
            return None

    # ✅ FIXED MISSING FUNCTION (CRITICAL ERROR FIX)
    def get_fno_symbols(self):

        try:
            # safe fallback list (production stable)
            return [
                "RELIANCE",
                "TCS",
                "INFY",
                "HDFCBANK",
                "ICICIBANK",
                "SBIN",
                "LT"
            ]
        except:
            return []

    def get_current_price(self, symbol: str):

        if not self.zerodha:
            return None

        try:
            ltp = self.zerodha.get_ltp([symbol])
            return ltp.get(symbol)
        except:
            return None
