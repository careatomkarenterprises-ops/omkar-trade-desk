"""
Zerodha Data Fetcher - Using Request Token (No Selenium)
"""

import os
import logging
import pandas as pd
import pickle
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class ZerodhaFetcher:
    def __init__(self):
        # Load credentials from GitHub Secrets
        self.api_key = os.getenv('ZERODHA_API_KEY')
        self.api_secret = os.getenv('ZERODHA_API_SECRET')
        self.request_token = os.getenv('ZERODHA_REQUEST_TOKEN')
        self.token_file = 'data/zerodha_session.pkl'
        
        # Validate credentials
        missing = []
        if not self.api_key: missing.append("ZERODHA_API_KEY")
        if not self.api_secret: missing.append("ZERODHA_API_SECRET")
        if not self.request_token: missing.append("ZERODHA_REQUEST_TOKEN")
        
        if missing:
            logger.error(f"Missing credentials: {', '.join(missing)}")
            raise ValueError(f"Missing credentials: {', '.join(missing)}")
        
        os.makedirs('data', exist_ok=True)
        self.kite = None
        self.access_token = None
        
        # Initialize connection
        self._initialize_connection()
        
        # Load instruments
        self.cache_file = 'data/zerodha_instruments.csv'
        self.instrument_cache = {}
        self.load_instruments()
        logger.info("✅ ZerodhaFetcher initialized successfully")

    def _initialize_connection(self):
        """Forces Auto-Login if the saved session is expired"""
        # 1. Try to reuse a session from the last 24 hours
        if self._load_session():
            logger.info("✅ Reusing existing session")
            return

        # 2. If no session, go STRAIGHT to Auto-Login (Skip manual request tokens)
        logger.info("🔄 Session expired. Starting Auto-Login engine...")
        self.access_token = self.get_automated_access_token()
        
        if self.access_token:
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            self._save_session()
            logger.info("✅ Auto-Login successful. Access Token saved.")
        else:
            logger.error("❌ Auto-Login failed. Check Credentials or TOTP Secret.")
            raise ValueError("Could not connect to Zerodha")

    def _save_session(self):
        """Save session to disk"""
        session_data = {
            'access_token': self.access_token,
            'api_key': self.api_key,
            'created_at': datetime.now().isoformat()
        }
        with open(self.token_file, 'wb') as f:
            pickle.dump(session_data, f)
        logger.info(f"✅ Session saved")

    def _load_session(self) -> bool:
        """Load and validate existing session"""
        if not os.path.exists(self.token_file):
            return False
        try:
            with open(self.token_file, 'rb') as f:
                data = pickle.load(f)
            
            # Check if session is less than 24 hours old
            created_at = datetime.fromisoformat(data['created_at'])
            if datetime.now() - created_at > timedelta(hours=23):
                logger.info("Session older than 23 hours, will refresh")
                return False
            
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(data['access_token'])
            # Validate token
            self.kite.profile()
            self.access_token = data['access_token']
            logger.info("✅ Session valid")
            return True
        except Exception as e:
            logger.warning(f"Session invalid: {e}")
            return False

    def refresh_if_needed(self):
        """Check if token is still valid"""
        try:
            if self.kite:
                self.kite.profile()
        except Exception as e:
            logger.warning(f"Token may be expired: {e}")
            self._initialize_connection()

    def load_instruments(self):
        """Load instrument list (updated daily)"""
        try:
            self.refresh_if_needed()
            
            if os.path.exists(self.cache_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
                if mod_time.date() == datetime.now().date():
                    logger.info("Using cached instruments")
                    return
            
            logger.info("Fetching fresh instrument list...")
            instruments = self.kite.instruments()
            df = pd.DataFrame(instruments)
            df.to_csv(self.cache_file, index=False)
            logger.info(f"✅ Loaded {len(df)} instruments")
            
        except Exception as e:
            logger.error(f"Error loading instruments: {e}")

    def get_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        """Get instrument token for a symbol"""
        try:
            self.refresh_if_needed()
            
            cache_key = f"{exchange}:{symbol}"
            if cache_key in self.instrument_cache:
                return self.instrument_cache[cache_key]
            
            df = pd.read_csv(self.cache_file)
            match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == symbol)]
            
            if match.empty and exchange == "NSE":
                match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == f"{symbol}EQ")]
            
            if not match.empty:
                token = str(match.iloc[0]['instrument_token'])
                self.instrument_cache[cache_key] = token
                return token
            
            logger.warning(f"No token found for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting token: {e}")
            return None

    def get_historical_data(self, symbol: str, interval: str = "day", days: int = 45) -> Optional[pd.DataFrame]:
        """Get historical candle data"""
        try:
            self.refresh_if_needed()
            
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
                df = df.rename(columns={
                    'date': 'Date', 'open': 'Open', 'high': 'High',
                    'low': 'Low', 'close': 'Close', 'volume': 'Volume'
                })
                df.set_index('Date', inplace=True)
                logger.info(f"✅ Got {len(df)} days for {symbol}")
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Data error for {symbol}: {e}")
            return None

    def get_ltp(self, symbols: List[str]) -> Dict:
        """Get last traded prices"""
        try:
            self.refresh_if_needed()
            formatted = [f"NSE:{s}" for s in symbols]
            ltp_data = self.kite.ltp(formatted)
            return {s: ltp_data[f"NSE:{s}"]['last_price'] for s in symbols if f"NSE:{s}" in ltp_data}
        except Exception as e:
            logger.error(f"LTP error: {e}")
            return {}

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote"""
        try:
            self.refresh_if_needed()
            quotes = self.kite.quote([f"NSE:{symbol}"])
            if quotes and f"NSE:{symbol}" in quotes:
                q = quotes[f"NSE:{symbol}"]
                return {
                    'symbol': symbol,
                    'last_price': q['last_price'],
                    'volume': q.get('volume', 0),
                    'open': q['ohlc']['open'],
                    'high': q['ohlc']['high'],
                    'low': q['ohlc']['low'],
                    'close': q['ohlc']['close'],
                    'timestamp': q['timestamp']
                }
            return None
        except Exception as e:
            logger.error(f"Quote error: {e}")
            return None
