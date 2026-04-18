import os
import logging
import pandas as pd
from kiteconnect import KiteConnect

logger = logging.getLogger(__name__)

# Global kite instance (lazy init)
_kite = None

def get_kite_instance():
    global _kite
    if _kite is None:
        api_key = os.getenv("KITE_API_KEY")
        access_token = os.getenv("KITE_ACCESS_TOKEN")
        if not api_key or not access_token:
            logger.error("KITE_API_KEY or KITE_ACCESS_TOKEN missing")
            return None
        _kite = KiteConnect(api_key=api_key)
        _kite.set_access_token(access_token)
    return _kite

def fetch_historical_data(symbol, interval="3minute", days=5):
    """
    Fetch historical data using Zerodha Kite API.
    interval: '3minute', '30minute', 'daily' (maps to '3minute', '30minute', 'day')
    days: number of days to fetch (max 1 year)
    Returns DataFrame with columns: open, high, low, close, volume
    """
    try:
        kite = get_kite_instance()
        if kite is None:
            logger.error("Kite instance not available")
            return None

        # Map interval to kite's interval strings
        interval_map = {
            "3minute": "3minute",
            "30minute": "30minute",
            "daily": "day",
            "1d": "day"
        }
        kite_interval = interval_map.get(interval, "3minute")

        # Convert symbol to instrument token (assume NSE equity format)
        # For NSE equity: symbol + "NSE" suffix? Kite expects 'NSE:RELIANCE'
        # We'll assume symbol is already in kite tradable format (e.g., 'RELIANCE')
        # For indices: 'NSE:NIFTY 50', 'NSE:BANK NIFTY'
        # For futures: 'NFO:NIFTY23NOVFUT' – you need to adjust based on your symbol list
        # Simpler: use kite.historical_data() with instrument_token – but we need token.
        # Alternative: use kite.quote() or kite.historical_data() with tradable symbol.
        
        # Convert symbol to kite tradable symbol:
        if symbol == "NIFTY":
            tradable_symbol = "NSE:NIFTY 50"
        elif symbol == "BANKNIFTY":
            tradable_symbol = "NSE:BANK NIFTY"
        elif symbol in ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]:
            tradable_symbol = f"NSE:{symbol}"
        else:
            # Assume it's an NSE equity
            tradable_symbol = f"NSE:{symbol}"

        # Calculate from_date (days back) and to_date (today)
        from_date = pd.Timestamp.now(tz='Asia/Kolkata') - pd.Timedelta(days=days)
        to_date = pd.Timestamp.now(tz='Asia/Kolkata')
        
        # Kite historical data returns list of dicts
        data = kite.historical_data(tradable_symbol, from_date, to_date, kite_interval)
        if not data:
            logger.warning(f"No historical data for {symbol}")
            return None
        
        df = pd.DataFrame(data)
        # Ensure column names are lowercase
        df.columns = [col.lower() for col in df.columns]
        # Required columns: open, high, low, close, volume
        required = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required):
            return df[required]
        else:
            logger.error(f"Missing columns in {symbol}: {df.columns}")
            return None
    except Exception as e:
        logger.error(f"Kite fetch error for {symbol}: {e}")
        return None
