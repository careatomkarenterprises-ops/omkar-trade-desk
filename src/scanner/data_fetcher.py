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


    # ================================
    # 🔥 CORE DATA FUNCTION (FIXED)
    # ================================
    def get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:

        if not self.zerodha:
            return None

        try:
            df = self.zerodha.get_historical_data(
                symbol,
                interval="day",   # you can later change dynamically
                days=45
            )

            if df is None or df.empty:
                return None

            # -------------------------------
            # ✅ NORMALIZE COLUMNS (CRITICAL FIX)
            # -------------------------------
            df.columns = [c.lower() for c in df.columns]

            df = df.rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume"
            })

            # -------------------------------
            # ✅ FINAL SAFETY CHECK
            # -------------------------------
            required = ["Open", "High", "Low", "Close", "Volume"]

            for col in required:
                if col not in df.columns:
                    logger.error(f"❌ Missing column {col} in {symbol}")
                    return None

            return df

        except Exception as e:
            logger.error(f"Fetch error {symbol}: {e}")
            return None


    # ================================
    # 📊 FNO SYMBOLS (SAFE FALLBACK)
    # ================================
    def get_fno_symbols(self):

        try:
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


    # ================================
    # 💰 LIVE PRICE
    # ================================
    def get_current_price(self, symbol: str):

        if not self.zerodha:
            return None

        try:
            ltp = self.zerodha.get_ltp([symbol])
            return ltp.get(symbol)
        except Exception as e:
            logger.error(f"LTP error {symbol}: {e}")
            return None
