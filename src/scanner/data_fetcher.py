import pandas as pd
import logging
from src.scanner import zerodha_fetcher as zf

logger = logging.getLogger(__name__)

def fetch_historical_data(symbol, interval="3minute", days=5):
    """
    Calls your existing zerodha_fetcher module.
    Assumes it has a function named 'get_historical_data' or 'fetch_historical_data'.
    If your function name is different, change it below.
    """
    try:
        # Try common function names – adjust according to your zerodha_fetcher.py
        if hasattr(zf, 'get_historical_data'):
            result = zf.get_historical_data(symbol, interval, days)
        elif hasattr(zf, 'fetch_historical_data'):
            result = zf.fetch_historical_data(symbol, interval, days)
        elif hasattr(zf, 'get_history'):
            result = zf.get_history(symbol, interval, days)
        else:
            logger.error("No suitable fetch function found in zerodha_fetcher")
            return None

        if result is None:
            return None

        # Convert result to DataFrame if needed
        if isinstance(result, pd.DataFrame):
            df = result
        elif isinstance(result, dict) and 'data' in result:
            df = pd.DataFrame(result['data'])
        elif isinstance(result, list):
            df = pd.DataFrame(result)
        else:
            return None

        if df.empty:
            return None

        df.columns = [col.lower() for col in df.columns]
        required = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required):
            return df[required]
        return None
    except Exception as e:
        logger.error(f"Zerodha fetch error {symbol}: {e}")
        return None
