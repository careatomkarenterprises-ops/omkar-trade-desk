"""
Zerodha Data Fetcher - Fully Automated Token Refresh
No Selenium, no daily manual updates!
Uses request_token (one-time setup) to generate fresh access_tokens automatically
"""

import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from typing import Optional, Dict, List
import pickle

logger = logging.getLogger(__name__)

class ZerodhaFetcher:
    """
    Fetch market data with automatic token refresh
    Uses request_token (one-time setup) to generate fresh access_tokens daily
    """
    
    def __init__(self):
        self.api_key = os.getenv('ZERODHA_API_KEY')
        self.api_secret = os.getenv('ZERODHA_API_SECRET')
        self.request_token = os.getenv('ZERODHA_REQUEST_TOKEN')
        
        if not self.api_key or not self.api_secret:
            logger.error("Zerodha credentials missing!")
            raise ValueError("ZERODHA_API_KEY and ZERODHA_API_SECRET required")
        
        if not self.request_token:
            logger.warning("ZERODHA_REQUEST_TOKEN not found. Will try to use existing session.")
        
        # Try to load saved session or create new
        self.token_file = 'data/zerodha_session.pkl'
        self.kite = None
        self.access_token = None
        
        # Initialize connection
        self._initialize_connection()
        
        # Setup data directory and cache
        os.makedirs('data', exist_ok=True)
        self.cache_file = 'data/zerodha_instruments.csv'
        self.instrument_cache = {}
        self.load_instruments()
        
        logger.info("✅ ZerodhaFetcher initialized with auto-refresh capability")
    
    def _initialize_connection(self):
        """Initialize or refresh the connection"""
        try:
            # Try to load existing session first
            if self._load_session():
                logger.info("✅ Loaded existing valid session")
                return
            
            # Create new session if we have request_token
            if self.request_token:
                logger.info("Generating new access token from request_token...")
                self._generate_access_token()
                self._save_session()
                return
            
            # No valid session and no request_token
            logger.error("No valid session and no request_token found!")
            logger.info("Please set ZERODHA_REQUEST_TOKEN secret (one-time setup)")
            raise ValueError("Cannot initialize connection")
            
        except Exception as e:
            logger.error(f"Connection initialization failed: {e}")
            raise
    
    def _generate_access_token(self):
        """Generate access token from request_token"""
        try:
            self.kite = KiteConnect(api_key=self.api_key)
            session = self.kite.generate_session(
                self.request_token, 
                api_secret=self.api_secret
            )
            self.access_token = session["access_token"]
            self.kite.set_access_token(self.access_token)
            logger.info("✅ New access token generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            raise
    
    def _save_session(self):
        """Save session to disk for reuse"""
        try:
            session_data = {
                'access_token': self.access_token,
                'created_at': datetime.now().isoformat(),
                'api_key': self.api_key
            }
            with open(self.token_file, 'wb') as f:
                pickle.dump(session_data, f)
            logger.info(f"✅ Session saved to {self.token_file}")
        except Exception as e:
            logger.warning(f"Could not save session: {e}")
    
    def _load_session(self) -> bool:
        """Load and validate existing session"""
        try:
            if not os.path.exists(self.token_file):
                return False
            
            with open(self.token_file, 'rb') as f:
                session_data = pickle.load(f)
            
            self.access_token = session_data['access_token']
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            
            # Validate token by making a test call
            self.kite.profile()
            logger.info("✅ Session validation successful")
            return True
            
        except Exception as e:
            logger.warning(f"Session validation failed: {e}")
            return False
    
    def refresh_if_needed(self):
        """Check and refresh token if expired"""
        try:
            if not self.kite:
                self._initialize_connection()
                return
            
            # Test current token
            self.kite.profile()
            logger.debug("Token is valid")
            
        except Exception as e:
            if "token" in str(e).lower() or "invalid" in str(e).lower():
                logger.warning("Token expired, refreshing...")
                if self.request_token:
                    self._generate_access_token()
                    self._save_session()
                else:
                    logger.error("Cannot refresh - no request_token available")
            else:
                logger.error(f"Unexpected error: {e}")
    
    def load_instruments(self):
        """Load instrument list (updated daily)"""
        try:
            if not self.kite:
                self.refresh_if_needed()
            
            if os.path.exists(self.cache_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
                if mod_time.date() == datetime.now().date():
                    logger.info("Using cached instruments from today")
                    return
            
            logger.info("Fetching fresh instrument list from Zerodha...")
            instruments = self.kite.instruments()
            
            df = pd.DataFrame(instruments)
            df.to_csv(self.cache_file, index=False)
            logger.info(f"✅ Loaded {len(df)} instruments to {self.cache_file}")
            
        except Exception as e:
            logger.error(f"Error loading instruments: {e}")
    
    def get_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        """Get instrument token for a symbol"""
        try:
            if not self.kite:
                self.refresh_if_needed()
            
            cache_key = f"{exchange}:{symbol}"
            if cache_key in self.instrument_cache:
                return self.instrument_cache[cache_key]
            
            if not os.path.exists(self.cache_file):
                self.load_instruments()
            
            df = pd.read_csv(self.cache_file)
            match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == symbol)]
            
            if not match.empty:
                token = str(match.iloc[0]['instrument_token'])
                self.instrument_cache[cache_key] = token
                return token
            
            # Try with EQ suffix for NSE
            if exchange == "NSE":
                match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == f"{symbol}EQ")]
                if not match.empty:
                    token = str(match.iloc[0]['instrument_token'])
                    self.instrument_cache[cache_key] = token
                    return token
            
            logger.warning(f"No instrument token found for {exchange}:{symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting token for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, interval: str = "day", days: int = 45) -> Optional[pd.DataFrame]:
        """Get historical candle data for pattern detection"""
        try:
            self.refresh_if_needed()
            
            token = self.get_instrument_token(symbol)
            if not token:
                logger.warning(f"No token found for {symbol}")
                return None
            
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            from_str = from_date.strftime("%Y-%m-%d %H:%M:%S")
            to_str = to_date.strftime("%Y-%m-%d %H:%M:%S")
            
            logger.debug(f"Fetching {interval} data for {symbol}")
            
            candles = self.kite.historical_data(
                instrument_token=int(token),
                from_date=from_str,
                to_date=to_str,
                interval=interval
            )
            
            if candles:
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
                df.attrs['source'] = 'zerodha'
                logger.info(f"✅ Got {len(df)} days of data for {symbol}")
                return df
            
            logger.warning(f"No candles returned for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_ltp(self, symbols: List[str]) -> Dict:
        """Get last traded prices for multiple symbols"""
        try:
            self.refresh_if_needed()
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
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol"""
        try:
            self.refresh_if_needed()
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
            logger.error(f"Error fetching quote: {e}")
            return None
    
    def get_ohlc(self, symbols: List[str]) -> Dict:
        """Get OHLC for multiple symbols"""
        try:
            self.refresh_if_needed()
            formatted = [f"NSE:{s}" for s in symbols]
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
