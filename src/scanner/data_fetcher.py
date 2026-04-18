import logging
from src.scanner.zerodha_fetcher import fetch_historical_data as zerodha_fetch

logger = logging.getLogger(__name__)

def fetch_historical_data(symbol, interval="3minute", days=5):
    """
    Wrapper around your existing zerodha_fetcher.fetch_historical_data.
    Ensures consistent return format (DataFrame with columns: open, high, low, close, volume).
    """
    try:
        df = zerodha_fetch(symbol, interval, days)
        if df is None or df.empty:
            logger.warning(f"No data for {symbol}")
            return None
        # Ensure columns are lowercase
        df.columns = [col.lower() for col in df.columns]
        required = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required):
            return df[required]
        else:
            logger.error(f"Missing columns in {symbol}: {df.columns}")
            return None
    except Exception as e:
        logger.error(f"Fetch error for {symbol}: {e}")
        return None
