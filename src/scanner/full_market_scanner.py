import pandas as pd
import time
import logging

from src.scanner.data_fetcher import DataFetcher
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


# ================================
# 📊 LOAD SYMBOLS
# ================================
def load_fno_symbols():
    try:
        df = pd.read_csv("fno_stocks.csv")

        if "symbol" in df.columns:
            symbols = df["symbol"].dropna().tolist()
        else:
            symbols = df.iloc[:, 0].dropna().tolist()

        logger.info(f"📊 Loaded F&O Symbols: {len(symbols)}")
        return symbols

    except Exception as e:
        logger.error(f"❌ CSV Load Error: {e}")
        return []


# ================================
# 🔥 YOUR VOLUME BREAKOUT STRATEGY
# ================================
def detect_volume_breakout(df):
    try:
        if df is None or df.empty or len(df) < 20:
            return None

        df = df.copy()

        # 15 SMA
        df["SMA15"] = df["Close"].rolling(15).mean()

        # Last 6 candles = setup zone
        setup = df.tail(6)

        high = setup["High"].max()
        low = setup["Low"].min()

        # Tight range condition (3%)
        range_pct = (high - low) / low
        if range_pct > 0.03:
            return None

        # Price near SMA
        last_close = df.iloc[-1]["Close"]
        sma = df.iloc[-1]["SMA15"]

        if pd.isna(sma):
            return None

        if abs(last_close - sma) / sma > 0.02:
            return None

        # Volume condition
        setup_vol_avg = setup["Volume"].mean()
        last_vol = df.iloc[-1]["Volume"]

        if setup_vol_avg == 0:
            return None

        # ONLY 40%–60% volume (your core logic)
        if not (0.4 * setup_vol_avg <= last_vol <= 0.6 * setup_vol_avg):
            return None

        # Breakout / Breakdown
        if last_close > high:
            return {
                "signal": "BUY_SIGNAL",
                "type": "VOLUME_BREAKOUT",
                "level": round(high, 2)
            }

        elif last_close < low:
            return {
                "signal": "SELL_SIGNAL",
                "type": "VOLUME_BREAKDOWN",
                "level": round(low, 2)
            }

        return None

    except Exception as e:
        logger.error(f"Pattern error: {e}")
        return None


# ================================
# 🚀 MAIN SCANNER
# ================================
def run_full_scan():

    fetcher = DataFetcher()
    telegram = TelegramPoster()

    symbols = load_fno_symbols()

    results = []
    scanned = 0

    logger.info("🚀 STARTING VOLUME BREAKOUT SCAN")

    for symbol in symbols:

        try:
            scanned += 1
            logger.info(f"🔍 Scanning: {symbol}")

            data = fetcher.get_stock_data(symbol)

            if data is None or data.empty:
                continue

            result = detect_volume_breakout(data)

            if result:
                output = {
                    "symbol": symbol,
                    "signal": result["signal"],
                    "level": result["level"]
                }

                results.append(output)

                logger.info(f"🔥 SIGNAL: {symbol} | {result['signal']}")

            time.sleep(0.2)

        except Exception as e:
            logger.error(f"{symbol} error: {e}")

    logger.info("📊 FULL SCAN COMPLETE")
    logger.info(f"Total Scanned: {scanned}")
    logger.info(f"Signals Generated: {len(results)}")

    # ================================
    # 📢 TELEGRAM OUTPUT
    # ================================
    if results:

        message = "🔥 <b>VOLUME BREAKOUT SETUPS</b>\n\n"

        for t in results[:10]:
            message += f"📊 <b>{t['symbol']}</b>\n"
            message += f"Signal: {t['signal']}\n"
            message += f"Level: {t['level']}\n\n"

        message += "⚠️ Based on Volume Compression Strategy"

        telegram.send_message("free", message)

    else:
        telegram.send_message(
            "free",
            "📊 Market Update:\n\n"
            "No valid volume breakout setups found.\n"
            "Market in compression / no clear move.\n\n"
            "👉 Wait for clean breakout."
        )

    return results


# ================================
# SAFE WRAPPER
# ================================
def run_full_market_scan():
    try:
        return run_full_scan()
    except Exception as e:
        logger.error(f"Wrapper error: {e}")
        return []


# ================================
# ENTRY POINT
# ================================
if __name__ == "__main__":
    run_full_scan()
