"""
Zerodha Data Fetcher - Using your paid Kite Connect API
"""

import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from typing import Optional, Dict, List
import time

logger = logging.getLogger(__name__)

class ZerodhaFetcher:
    """
    Fetch market data using Zerodha Kite Connect API
    Requires paid subscription (₹500/month)
    """
    
    def __init__(self):
        self.api_key = os.getenv('ZERODHA_API_KEY')
        self.access_token = os.getenv('KITE_ACCESS_TOKEN')
        
        if not self.api_key or not self.access_token:
            logger.error("Zerodha credentials missing!")
            raise ValueError("ZERODHA_API_KEY and ZERODHA_ACCESS_TOKEN required")
        
        # Initialize Kite Connect
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        
        # Cache for instrument tokens
        self.instrument_cache = {}
        self.cache_file = 'data/zerodha_instruments.csv'
        self.load_instruments()
        
        logger.info("✅ ZerodhaFetcher initialized with paid API")
    
    def load_instruments(self):
        """Load instrument list (updated daily)"""
        try:
            if os.path.exists(self.cache_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
                if mod_time.date() == datetime.now().date():
                    return
            
            instruments = self.kite.instruments()
            df = pd.DataFrame(instruments)
            os.makedirs('data', exist_ok=True)
            df.to_csv(self.cache_file, index=False)
            logger.info(f"Loaded {len(df)} instruments")
        except Exception as e:
            logger.error(f"Error loading instruments: {e}")
    
    def get_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        """Get instrument token for a symbol"""
        try:
            cache_key = f"{exchange}:{symbol}"
            if cache_key in self.instrument_cache:
                return self.instrument_cache[cache_key]
            
            df = pd.read_csv(self.cache_file)
            match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == symbol)]
            
            if not match.empty:
                token = str(match.iloc[0]['instrument_token'])
                self.instrument_cache[cache_key] = token
                return token
            return None
        except Exception as e:
            logger.error(f"Error getting token for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, interval: str = "day", days: int = 45) -> Optional[pd.DataFrame]:
        """Get historical candle data from Zerodha"""
        try:
            token = self.get_instrument_token(symbol)
            if not token: return None
            
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            candles = self.kite.historical_data(
                instrument_token=int(token),
                from_date=from_date.strftime("%Y-%m-%d %H:%M:%S"),
                to_date=to_date.strftime("%Y-%m-%d %H:%M:%S"),
                interval=interval
            )
            
            if candles:
                df = pd.DataFrame(candles)
                df.set_index('date', inplace=True)
                return df
            return None
        except Exception as e:
            logger.error(f"Historical data error for {symbol}: {e}")
            return None
    
    def get_ltp(self, symbols: List[str]) -> Dict:
        """Get only last traded prices"""
        try:
            formatted = [f"NSE:{s}" for s in symbols]
            ltp_data = self.kite.ltp(formatted)
            return {s: ltp_data[f"NSE:{s}"]['last_price'] for s in symbols if f"NSE:{s}" in ltp_data}
        except Exception as e:
            logger.error(f"LTP error: {e}")
            return {}
