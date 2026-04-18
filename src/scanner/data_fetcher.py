import pandas as pd
import logging
from src.scanner import zerodha_fetcher as zf

logger = logging.getLogger(__name__)

# ============================================================
# 👇 EDIT THIS LINE – change to the ACTUAL function name in your zerodha_fetcher.py
# ============================================================
CORRECT_FUNCTION_NAME = "get_historical_data"   # <-- CHANGE THIS
# ============================================================

def fetch_historical_data(symbol, interval="3minute", days=5):
    """
    Calls your existing zerodha_fetcher module.
    """
    try:
        # First, try the user‑specified function name
        if hasattr(zf, CORRECT_FUNCTION_NAME):
            fetch_func = getattr(zf, CORRECT_FUNCTION_NAME)
            logger.info(f"Using zerodha_fetcher.{CORRECT_FUNCTION_NAME}")
            result = fetch_func(symbol, interval, days)
        else:
            # If not found, scan all functions in zerodha_fetcher for debugging
            available_funcs = [name for name in dir(zf) if callable(getattr(zf, name)) and not name.startswith('_')]
            logger.error(f"Function '{CORRECT_FUNCTION_NAME}' not found in zerodha_fetcher.")
            logger.error(f"Available functions: {available_funcs}")
            logger.error("Please update CORRECT_FUNCTION_NAME in data_fetcher.py to match one of these.")
            return None

        if result is None:
            return None

        # Normalise result to DataFrame
        if isinstance(result, pd.DataFrame):
            df = result
        elif isinstance(result, dict) and 'data' in result:
            df = pd.DataFrame(result['data'])
        elif isinstance(result, list):
            df = pd.DataFrame(result)
        else:
            logger.error(f"Unexpected result type from {CORRECT_FUNCTION_NAME}: {type(result)}")
            return None

        if df.empty:
            return None

        df.columns = [col.lower() for col in df.columns]
        required = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required):
            return df[required]
        else:
            logger.error(f"Missing columns in {symbol}: {df.columns}")
            return None
    except Exception as e:
        logger.error(f"Zerodha fetch error {symbol}: {e}")
        return None
