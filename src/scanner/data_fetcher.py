import os
import logging
import pandas as pd
from kiteconnect import KiteConnect

logger = logging.getLogger(__name__)

_kite = None
_instrument_cache = None

def get_kite_instance():
    global _kite
    if _kite is None:
        api_key = os.getenv("KITE_API_KEY")
        access_token = os.getenv("KITE_ACCESS_TOKEN")
        if not api_key or not access_token:
            logger.error("Missing KITE_API_KEY or KITE_ACCESS_TOKEN")
            return None
        _kite = KiteConnect(api_key=api_key)
        _kite.set_access_token(access_token)
    return _kite

def get_instrument_token(symbol, exchange="NSE"):
    """Get instrument token for a given symbol and exchange."""
    global _instrument_cache
    kite = get_kite_instance()
    if kite is None:
        return None
    if _instrument_cache is None:
        try:
            instruments = kite.instruments(exchange)
            _instrument_cache = {inst['tradingsymbol']: inst['instrument_token'] for inst in instruments}
        except Exception as e:
            logger.error(f"Failed to fetch instruments: {e}")
            return None
    # Try exact match
    if symbol in _instrument_cache:
        return _instrument_cache[symbol]
    # Try with exchange prefix
    full_symbol = f"{exchange}:{symbol}"
    if full_symbol in _instrument_cache:
        return _instrument_cache[full_symbol]
    # Try without exchange
    for key, token in _instrument_cache.items():
        if key.endswith(symbol):
            return token
    return None

def fetch_historical_data(symbol, interval="3minute", days=5):
    """
    Fetch historical data using Zerodha Kite API.
    Returns DataFrame with columns: open, high, low, close, volume
    """
    try:
        kite = get_kite_instance()
        if kite is None:
            return None
        
        # Map interval
        interval_map = {
            "3minute": "3minute",
            "30minute": "30minute",
            "daily": "day"
        }
        kite_interval = interval_map.get(interval, "3minute")
        
        # Get instrument token
        # For indices, exchange = "NSE" works for NIFTY 50, BANK NIFTY
        exchange = "NSE"
        if symbol in ["NIFTY", "BANKNIFTY"]:
            # Kite uses "NSE:NIFTY 50" etc.
            if symbol == "NIFTY":
                tradingsymbol = "NIFTY 50"
            else:
                tradingsymbol = "BANK NIFTY"
        else:
            tradingsymbol = symbol
        
        instrument_token = get_instrument_token(tradingsymbol, exchange)
        if not instrument_token:
            logger.warning(f"No instrument token for {symbol}")
            return None
        
        from_date = pd.Timestamp.now(tz='Asia/Kolkata') - pd.Timedelta(days=days)
        to_date = pd.Timestamp.now(tz='Asia/Kolkata')
        
        data = kite.historical_data(instrument_token, from_date, to_date, kite_interval)
        if not data:
            return None
        
        df = pd.DataFrame(data)
        df.columns = [col.lower() for col in df.columns]
        required = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required):
            return df[required]
        return None
    except Exception as e:
        logger.error(f"Kite fetch error {symbol}: {e}")
        return None
