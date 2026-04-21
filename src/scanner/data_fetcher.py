import pandas as pd
import yfinance as yf
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

# 🔹 Symbol Mapping (Index, Currency, Commodity)
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


# 🔹 Convert symbol safely (Fix .NS.NS issue)
def convert_symbol(symbol):
    symbol = symbol.upper().strip()

    # If already mapped (index/currency/commodity)
    if symbol in SYMBOL_MAP:
        return SYMBOL_MAP[symbol]

    # If already ends with .NS → don't add again
    if symbol.endswith(".NS"):
        return symbol

    return f"{symbol}.NS"


# 🔹 Fetch Historical Data (SAFE + RETRY)
def fetch_historical_data(symbol, interval="5minute", days=5):
    try:
        yf_symbol = convert_symbol(symbol)

        interval_map = {
            "1minute": "1m",
            "3minute": "5m",   # yfinance limitation
            "5minute": "5m",
            "15minute": "15m",
            "30minute": "30m",
            "day": "1d"
        }

        yf_interval = interval_map.get(interval, "5m")

        end = datetime.now()
        start = end - timedelta(days=days)

        # 🔁 Retry logic (important for yfinance stability)
        for attempt in range(2):
            try:
                df = yf.download(
                    yf_symbol,
                    start=start,
                    end=end,
                    interval=yf_interval,
                    progress=False,
                    threads=False
                )

                if df is not None and not df.empty:
                    break

            except Exception as e:
                logger.warning(f"Retry {attempt+1} failed for {yf_symbol}: {e}")
                time.sleep(1)

        # ❌ Still no data
        if df is None or df.empty:
            logger.warning(f"No data for {symbol} ({yf_symbol})")
            return None

        # 🔹 Normalize columns
        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })

        # 🔹 Ensure required columns exist
        required_cols = ["open", "high", "low", "close", "volume"]
        if not all(col in df.columns for col in required_cols):
            logger.warning(f"Missing columns for {symbol}")
            return None

        return df[required_cols]

    except Exception as e:
        logger.error(f"Fetch error {symbol}: {e}")
        return None


# 🔹 Get Latest Price (SAFE)
def get_ltp(symbol):
    try:
        yf_symbol = convert_symbol(symbol)

        data = yf.Ticker(yf_symbol).history(period="1d", interval="1m")

        if data is None or data.empty:
            return None

        return float(data["Close"].iloc[-1])

    except Exception as e:
        logger.warning(f"LTP fetch failed for {symbol}: {e}")
        return None
