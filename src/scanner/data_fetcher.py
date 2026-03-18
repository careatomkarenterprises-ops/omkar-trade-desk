"""
Data Fetcher - Yahoo Finance Only with Retry Logic
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import logging
from typing import Optional, Dict
from pathlib import Path
import random

logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Fetch market data from Yahoo Finance with retry logic
    """
    
    def __init__(self):
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = 600  # 10 minutes cache (increased from 5)
        self.request_delay = 1.0  # 1 second delay between requests (increased)
        self.max_retries = 3  # Number of retry attempts
        
        # Symbol mappings (same as before)
        self.symbol_map = {
            'NIFTY 50': '^NSEI',
            'BANK NIFTY': '^NSEBANK',
            'GOLD': 'GC=F',
            'SILVER': 'SI=F',
            'CRUDEOIL': 'CL=F',
            'USDINR': 'INR=X',
        }
        
        # Reduced stock list to prevent rate limiting
        self.nifty_stocks = {
            'RELIANCE': 'RELIANCE.NS',
            'TCS': 'TCS.NS',
            'HDFCBANK': 'HDFCBANK.NS',
            'INFY': 'INFY.NS',
            'ICICIBANK': 'ICICIBANK.NS',
            'SBIN': 'SBIN.NS',
            'ITC': 'ITC.NS',
            'LT': 'LT.NS',
        }
        
        logger.info("DataFetcher initialized with retry logic")
    
    def fetch_data_with_retry(self, symbol: str, period: str = "5d", interval: str = "15m", attempt: int = 1) -> Optional[pd.DataFrame]:
        """
        Fetch data with retry logic
        """
        try:
            # Get proper Yahoo symbol
            yahoo_symbol = self.get_yahoo_symbol(symbol)
            
            # Check cache first
            cache_file = self.cache_dir / f"{yahoo_symbol}_{period}_{interval}.parquet"
            if cache_file.exists():
                modified_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if (datetime.now() - modified_time).seconds < self.cache_duration:
                    logger.debug(f"Using cached data for {symbol}")
                    return pd.read_parquet(cache_file)
            
            # Add jitter to delay to avoid rate limiting
            time.sleep(self.request_delay + random.uniform(0, 0.5))
            
            # Fetch from Yahoo Finance
            logger.info(f"Fetching {symbol} as {yahoo_symbol} (attempt {attempt})")
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data for {symbol}")
                return None
            
            # Cache the data
            data.to_parquet(cache_file)
            logger.info(f"Successfully fetched {symbol} - {len(data)} rows")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching {symbol} (attempt {attempt}): {e}")
            
            # Retry logic
            if attempt < self.max_retries:
                wait_time = 5 * attempt  # Exponential backoff: 5s, 10s, 15s
                logger.info(f"Retrying {symbol} in {wait_time} seconds...")
                time.sleep(wait_time)
                return self.fetch_data_with_retry(symbol, period, interval, attempt + 1)
            else:
                logger.error(f"Failed to fetch {symbol} after {self.max_retries} attempts")
                return None
    
    def get_yahoo_symbol(self, symbol: str) -> str:
        """Convert common symbol names to Yahoo Finance symbols"""
        if symbol in self.symbol_map:
            return self.symbol_map[symbol]
        if symbol in self.nifty_stocks:
            return self.nifty_stocks[symbol]
        if not symbol.endswith(('.NS', '.BO', '=F', '^')):
            return f"{symbol}.NS"
        return symbol
    
    def get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get stock data with retry logic"""
        return self.fetch_data_with_retry(symbol, period="5d", interval="15m")
