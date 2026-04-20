import pandas as pd
import logging
from src.scanner import zerodha_fetcher as zf

logger = logging.getLogger(__name__)


def fetch_historical_data(symbol, interval="3minute", days=5):
    try:
        if not hasattr(zf, 'ZerodhaFetcher'):
            logger.error("ZerodhaFetcher class not found")
            return None

        fetcher = zf.ZerodhaFetcher()

        possible_methods = [
            'get_historical_data',
            'historical_data',
            'get_history',
            'fetch_historical_data',
            'get_ohlcv',
            'fetch_data'
        ]

        fetch_method = None
        for method_name in possible_methods:
            if hasattr(fetcher, method_name):
                fetch_method = getattr(fetcher, method_name)
                logger.info(f"Using method: {method_name}")
                break

        if fetch_method is None:
            methods = [
                name for name in dir(fetcher)
                if callable(getattr(fetcher, name)) and not name.startswith('_')
            ]
            logger.error(f"No fetch method found. Available: {methods}")
            return None

        result = fetch_method(symbol, interval, days)

        if result is None:
            return None

        if isinstance(result, pd.DataFrame):
            df = result
        elif isinstance(result, dict) and 'data' in result:
            df = pd.DataFrame(result['data'])
        elif isinstance(result, list):
            df = pd.DataFrame(result)
        else:
            logger.error(f"Unexpected type: {type(result)}")
            return None

        if df.empty:
            return None

        df.columns = [col.lower() for col in df.columns]

        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required_cols):
            return df[required_cols]

        logger.error(f"Missing required columns in {symbol}: {df.columns}")
        return None

    except Exception as e:
        logger.error(f"Fetch error {symbol}: {e}")
        return None
