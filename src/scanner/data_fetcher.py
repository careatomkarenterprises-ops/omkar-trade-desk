"""
Data Fetcher - Yahoo Finance Only
NO ZERODHA TOKEN NEEDED - 100% AUTOMATED
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, Optional, List
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Fetch market data from Yahoo Finance
    No authentication required - works 24/7 automatically
    """
    
    def __init__(self):
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = 300  # 5 minutes cache
        self.request_delay = 0.5  # Rate limiting delay
        
        # Symbol mappings for Yahoo Finance
        self.symbol_map = {
            # Indices
            'NIFTY 50': '^NSEI',
            'BANK NIFTY': '^NSEBANK',
            'SENSEX': '^BSESN',
            'NIFTY IT': '^CNXIT',
            
            # Commodities
            'GOLD': 'GC=F',
            'SILVER': 'SI=F',
            'CRUDEOIL': 'CL=F',
            'NATURALGAS': 'NG=F',
            
            # Forex
            'USDINR': 'INR=X',
            'EURINR': 'EURINR=X',
            'GBPINR': 'GBPINR=X',
            'JPYINR': 'JPYINR=X',
            
            # US Markets
            'DOW': '^DJI',
            'S&P500': '^GSPC',
            'NASDAQ': '^IXIC'
        }
        
        # Nifty 50 stocks (top ones)
        self.nifty_stocks = {
            'RELIANCE': 'RELIANCE.NS',
            'TCS': 'TCS.NS',
            'HDFCBANK': 'HDFCBANK.NS',
            'INFY': 'INFY.NS',
            'ICICIBANK': 'ICICIBANK.NS',
            'SBIN': 'SBIN.NS',
            'BHARTIARTL': 'BHARTIARTL.NS',
            'ITC': 'ITC.NS',
            'LT': 'LT.NS',
            'SUNPHARMA': 'SUNPHARMA.NS',
            'AXISBANK': 'AXISBANK.NS',
            'KOTAKBANK': 'KOTAKBANK.NS',
            'HCLTECH': 'HCLTECH.NS',
            'TATASTEEL': 'TATASTEEL.NS',
            'MARUTI': 'MARUTI.NS',
            'TITAN': 'TITAN.NS',
            'WIPRO': 'WIPRO.NS',
            'ONGC': 'ONGC.NS',
            'NTPC': 'NTPC.NS',
            'POWERGRID': 'POWERGRID.NS'
        }
        
        logger.info("DataFetcher initialized - No authentication required")
    
    def get_yahoo_symbol(self, symbol: str) -> str:
        """Convert common symbol names to Yahoo Finance symbols"""
        # Check if it's a special symbol
        if symbol in self.symbol_map:
            return self.symbol_map[symbol]
        
        # Check if it's a Nifty stock
        if symbol in self.nifty_stocks:
            return self.nifty_stocks[symbol]
        
        # Default: add .NS for NSE stocks
        if not symbol.endswith(('.NS', '.BO', '=F', '^')):
            return f"{symbol}.NS"
        
        return symbol
    
    def fetch_data(self, symbol: str, period: str = "1mo", interval: str = "15m") -> Optional[pd.DataFrame]:
        """
        Fetch data from Yahoo Finance
        No token needed - works automatically
        """
        try:
            # Get proper Yahoo symbol
            yahoo_symbol = self.get_yahoo_symbol(symbol)
            
            # Check cache
            cache_file = self.cache_dir / f"{yahoo_symbol}_{period}_{interval}.parquet"
            if cache_file.exists():
                modified_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if (datetime.now() - modified_time).seconds < self.cache_duration:
                    logger.debug(f"Using cached data for {symbol}")
                    return pd.read_parquet(cache_file)
            
            # Rate limiting
            time.sleep(self.request_delay)
            
            # Fetch from Yahoo Finance
            logger.info(f"Fetching {symbol} as {yahoo_symbol}")
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
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get stock data with default parameters"""
        return self.fetch_data(symbol, period="1mo", interval="15m")
    
    def get_index_data(self, index_name: str) -> Optional[pd.DataFrame]:
        """Get index data"""
        return self.fetch_data(index_name, period="1mo", interval="15m")
    
    def get_commodity_data(self, commodity: str) -> Optional[pd.DataFrame]:
        """Get commodity data"""
        return self.fetch_data(commodity, period="1mo", interval="1h")
    
    def get_forex_data(self, pair: str) -> Optional[pd.DataFrame]:
        """Get forex data"""
        return self.fetch_data(pair, period="1mo", interval="1h")
    
    def get_all_indices(self) -> Dict[str, pd.DataFrame]:
        """Fetch all major indices"""
        indices = ['NIFTY 50', 'BANK NIFTY', 'SENSEX']
        result = {}
        for idx in indices:
            data = self.get_index_data(idx)
            if data is not None:
                result[idx] = data
        return result
    
    def get_all_commodities(self) -> Dict[str, pd.DataFrame]:
        """Fetch all commodities"""
        commodities = ['GOLD', 'SILVER', 'CRUDEOIL']
        result = {}
        for comm in commodities:
            data = self.get_commodity_data(comm)
            if data is not None:
                result[comm] = data
        return result
