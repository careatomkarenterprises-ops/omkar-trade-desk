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
        self.access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
        
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
                # Check if cache is from today
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
                if mod_time.date() == datetime.now().date():
                    logger.info("Using cached instruments")
                    return
            
            # Fetch fresh instruments (Zerodha recommends once daily at 8:30 AM) [citation:7]
            logger.info("Fetching fresh instrument list from Zerodha...")
            instruments = self.kite.instruments()
            
            # Convert to DataFrame for easier lookup
            df = pd.DataFrame(instruments)
            df.to_csv(self.cache_file, index=False)
            logger.info(f"Loaded {len(df)} instruments")
            
        except Exception as e:
            logger.error(f"Error loading instruments: {e}")
    
    def get_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        """Get instrument token for a symbol"""
        try:
            # Check cache first
            cache_key = f"{exchange}:{symbol}"
            if cache_key in self.instrument_cache:
                return self.instrument_cache[cache_key]
            
            # Load instruments and find token
            df = pd.read_csv(self.cache_file)
            
            # Filter by exchange and symbol
            match = df[(df['exchange'] == exchange) & 
                      (df['tradingsymbol'] == symbol)]
            
            if not match.empty:
                token = str(match.iloc[0]['instrument_token'])
                self.instrument_cache[cache_key] = token
                return token
            
            # Try with .NS suffix for NSE
            if exchange == "NSE" and not symbol.endswith(".NS"):
                return self.get_instrument_token(symbol + ".NS", exchange)
            
            logger.warning(f"No instrument token found for {exchange}:{symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting token for {symbol}: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol [citation:2]"""
        try:
            token = self.get_instrument_token(symbol)
            if not token:
                return None
            
            # Get quote using instrument token or exchange:symbol format
            quotes = self.kite.quote([f"NSE:{symbol}"])
            
            if quotes and f"NSE:{symbol}" in quotes:
                quote = quotes[f"NSE:{symbol}"]
                
                return {
                    'symbol': symbol,
                    'last_price': quote['last_price'],
                    'volume': quote.get('volume', 0),
                    'open': quote['ohlc']['open'],
                    'high': quote['ohlc']['high'],
                    'low': quote['ohlc']['low'],
                    'close': quote['ohlc']['close'],
                    'change': quote['net_change'],
                    'change_pct': (quote['net_change'] / quote['ohlc']['close']) * 100 if quote['ohlc']['close'] else 0,
                    'timestamp': quote['timestamp'],
                    'source': 'zerodha'
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, interval: str = "15minute", days: int = 5) -> Optional[pd.DataFrame]:
        """Get historical candle data [citation:3]"""
        try:
            token = self.get_instrument_token(symbol)
            if not token:
                return None
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Format dates as required by Zerodha
            from_str = from_date.strftime("%Y-%m-%d %H:%M:%S")
            to_str = to_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get historical data
            # Note: interval can be "minute", "3minute", "5minute", "10minute", "15minute", "30minute", "60minute", "day" [citation:2]
            candles = self.kite.historical_data(
                instrument_token=int(token),
                from_date=from_str,
                to_date=to_str,
                interval=interval
            )
            
            if candles:
                # Convert to DataFrame (same format as yfinance for compatibility)
                df = pd.DataFrame(candles)
                df = df.rename(columns={
                    'date': 'Date',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                })
                df.set_index('Date', inplace=True)
                df.sort_index(inplace=True)
                
                # Add metadata
                df.attrs['source'] = 'zerodha'
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_ohlc(self, symbols: List[str]) -> Dict:
        """Get OHLC for multiple symbols in one call [citation:7]"""
        try:
            # Format symbols for Zerodha
            formatted = [f"NSE:{s}" for s in symbols]
            
            # Get OHLC (lighter than full quote)
            ohlc_data = self.kite.ohlc(formatted)
            
            result = {}
            for sym in symbols:
                key = f"NSE:{sym}"
                if key in ohlc_data:
                    data = ohlc_data[key]
                    result[sym] = {
                        'last_price': data['last_price'],
                        'open': data['ohlc']['open'],
                        'high': data['ohlc']['high'],
                        'low': data['ohlc']['low'],
                        'close': data['ohlc']['close']
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching OHLC: {e}")
            return {}
    
    def get_ltp(self, symbols: List[str]) -> Dict:
        """Get only last traded prices (lightest API call) [citation:3]"""
        try:
            formatted = [f"NSE:{s}" for s in symbols]
            ltp_data = self.kite.ltp(formatted)
            
            result = {}
            for sym in symbols:
                key = f"NSE:{sym}"
                if key in ltp_data:
                    result[sym] = ltp_data[key]['last_price']
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching LTP: {e}")
            return {}
