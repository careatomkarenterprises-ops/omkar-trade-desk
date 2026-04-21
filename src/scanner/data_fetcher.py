import pandas as pd
import yfinance as yf
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ---------------- SYMBOL MAPPING ----------------
SYMBOL_MAP = {
    "NIFTY 50": "^NSEI",
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "BANK NIFTY": "^NSEBANK",
    "FINNIFTY": "^NSEFIN",
    "SENSEX": "^BSESN",
    "USDINR": "USDINR=X",
    "CRUDE": "CL=F",
    "GOLD": "GC=F",
    "SILVER": "SI=F"
}

def convert_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()

    # If already mapped
    if symbol in SYMBOL_MAP:
        return SYMBOL_MAP[symbol]

    # Default: NSE stock
    if not symbol.endswith(".NS"):
        return f"{symbol}.NS"

    return symbol


# ---------------- MAIN FETCH FUNCTION ----------------
def fetch_historical_data(symbol, interval="5m", days=5):
    try:
        yf_symbol = convert_symbol(symbol)

        logger.info(f"Fetching {symbol} → {yf_symbol}")

        # Interval mapping (Zerodha → yfinance)
        interval_map = {
            "1minute": "1m",
            "3minute": "5m",   # closest available
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
            logger.warning(f"No data for {symbol}")
            return None

        # Standardize column names
        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })

        required_cols = ['open', 'high', 'low', 'close', 'volume']

        if not all(col in df.columns for col in required_cols):
            logger.error(f"Missing columns for {symbol}: {df.columns}")
            return None

        df = df[required_cols]

        return df

    except Exception as e:
        logger.error(f"Fetch error {symbol}: {e}")
        return None


# ---------------- OPTIONAL: LIVE PRICE ----------------
def get_ltp(symbol):
    try:
        yf_symbol = convert_symbol(symbol)

        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            return None

        return float(data["Close"].iloc[-1])

    except Exception as e:
        logger.error(f"LTP error {symbol}: {e}")
        return None
