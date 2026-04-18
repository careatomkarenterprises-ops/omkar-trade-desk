import pandas as pd
import logging
from src.scanner import zerodha_fetcher as zf

logger = logging.getLogger(__name__)

def fetch_historical_data(symbol, interval="3minute", days=5):
    """
    Calls your ZerodhaFetcher class instance to get historical data.
    Auto‑detects the correct method name.
    """
    try:
        # 1. Check if zerodha_fetcher has a ZerodhaFetcher class
        if not hasattr(zf, 'ZerodhaFetcher'):
            logger.error("ZerodhaFetcher class not found in zerodha_fetcher module")
            return None

        # 2. Create an instance (assume no constructor arguments or uses env)
        fetcher = zf.ZerodhaFetcher()

        # 3. List of possible method names for fetching historical data
        possible_methods = [
            'get_historical_data',
            'historical_data',
            'get_history',
            'fetch_historical_data',
            'get_ohlcv',
            'fetch_data'
        ]

        # 4. Find the first method that exists
        fetch_method = None
        for method_name in possible_methods:
            if hasattr(fetcher, method_name):
                fetch_method = getattr(fetcher, method_name)
                logger.info(f"Using ZerodhaFetcher.{method_name}")
                break

        if fetch_method is None:
            # Debug: list all callable methods of the instance
            methods = [name for name in dir(fetcher) if callable(getattr(fetcher, name)) and not name.startswith('_')]
            logger.error(f"No known fetch method found. Available methods: {methods}")
            return None

        # 5. Call the method with symbol, interval, days (adjust if signature differs)
        result = fetch_method(symbol, interval, days)

        if result is None:
            return None

        # 6. Normalise result to DataFrame
        if isinstance(result, pd.DataFrame):
            df = result
        elif isinstance(result, dict) and 'data' in result:
            df = pd.DataFrame(result['data'])
        elif isinstance(result, list):
            df = pd.DataFrame(result)
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            return None

        if df.empty:
            return None

        # 7. Ensure column names are lowercase and required columns exist
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
