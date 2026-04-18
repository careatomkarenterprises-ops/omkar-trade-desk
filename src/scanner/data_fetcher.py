import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_historical_data(symbol, interval="daily", days=5):
    """
    Fetch historical data using yfinance.
    interval: '1m', '5m', '15m', '30m', '1h', '1d'
    days: number of days to fetch
    """
    try:
        # Map interval to yfinance string
        interval_map = {
            "3minute": "5m",    # yfinance doesn't have 3m, use 5m
            "30minute": "30m",
            "daily": "1d",
            "1d": "1d"
        }
        yf_interval = interval_map.get(interval, "5m")
        # yfinance expects period like "5d"
        period = f"{days+2}d"
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=yf_interval)
        if df.empty:
            logger.warning(f"No data for {symbol}")
            return None
        # Ensure required columns exist
        df = df.rename(columns=str.lower)
        required = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in required):
            return df[required]
        else:
            logger.error(f"Missing columns in {symbol}: {df.columns}")
            return None
    except Exception as e:
        logger.error(f"yfinance error for {symbol}: {e}")
        return None
