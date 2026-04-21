import pandas as pd
import yfinance as yf
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SYMBOL_MAP = {
    "NIFTY 50": "^NSEI",
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "BANK NIFTY": "^NSEBANK",
    "FINNIFTY": "^NSEFIN",
    "SENSEX": "^BSESN",
    "USDINR": "USDINR=X",
    "EURINR": "EURINR=X",
    "GBPINR": "GBPINR=X",
    "JPYINR": "JPYINR=X",
    "CRUDE": "CL=F",
    "GOLD": "GC=F",
    "SILVER": "SI=F"
}

def convert_symbol(symbol):
    symbol = symbol.upper().strip()
    if symbol in SYMBOL_MAP:
        return SYMBOL_MAP[symbol]
    return f"{symbol}.NS"

def fetch_historical_data(symbol, interval="5minute", days=5):
    try:
        yf_symbol = convert_symbol(symbol)

        interval_map = {
            "1minute": "1m",
            "3minute": "5m",
            "5minute": "5m",
            "15minute": "15m",
            "30minute": "30m",
            "day": "1d"
        }

        yf_interval = interval_map.get(interval, "5m")

        end = datetime.now()
        start = end - timedelta(days=days)

        df = yf.download(
            yf_symbol,
            start=start,
            end=end,
            interval=yf_interval,
            progress=False
        )

        if df is None or df.empty:
            return None

        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })

        return df[['open', 'high', 'low', 'close', 'volume']]

    except Exception as e:
        logger.error(f"Fetch error {symbol}: {e}")
        return None


def get_ltp(symbol):
    try:
        yf_symbol = convert_symbol(symbol)
        data = yf.Ticker(yf_symbol).history(period="1d", interval="1m")
        if data.empty:
            return None
        return float(data["Close"].iloc[-1])
    except:
        return None
