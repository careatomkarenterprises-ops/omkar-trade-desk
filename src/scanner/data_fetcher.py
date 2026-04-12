"""
Data Fetcher - Zerodha Exclusive Production Version
Strictly uses paid Kite Connect API for F&O Stocks.
"""

import logging
import pandas as pd
from typing import Optional
from src.scanner.zerodha_fetcher import ZerodhaFetcher

logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Fetch market data - Zerodha Exclusive.
    No Yahoo Fallback to ensure 100% data integrity for VSA logic.
    """
    
    def __init__(self):
        self.zerodha = None
        try:
            self.zerodha = ZerodhaFetcher()
            logger.info("✅ Zerodha API Connection Active")
        except Exception as e:
            logger.critical("❌ Technical Issue: Zerodha API Initialization Failed")
            self.zerodha = None
    
    def is_ready(self) -> bool:
        """Check if API is active before starting scan"""
        return self.zerodha is not None

    def get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Fetches live DAILY data from Zerodha.
        Required for 15-day Volume SMA + 6-day Quiet Period analysis.
        """
        if not self.zerodha:
            return None

        try:
            # We fetch 45 days to ensure enough data for a 15-day SMA calculation
            df = self.zerodha.get_historical_data(symbol, interval="day", days=45)
            
            if df is not None and not df.empty:
                # Standardize columns to lowercase for the PatternDetector
                df.columns = [c.lower() for c in df.columns]
                return df
            
            logger.warning(f"No live data returned for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Zerodha API Fetch Error for {symbol}: {e}")
            return None

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Fetch real-time LTP via Zerodha"""
        if not self.zerodha:
            return None
        try:
            ltp_dict = self.zerodha.get_ltp([symbol])
            return ltp_dict.get(symbol)
        except:
            return None
