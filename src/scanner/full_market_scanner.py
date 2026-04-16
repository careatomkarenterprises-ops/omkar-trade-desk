import pandas as pd
import time
import logging

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


# ---------------- LOAD SYMBOLS ----------------

def load_fno_symbols():
    try:
        df = pd.read_csv("fno_stocks.csv")

        symbols = df["symbol"].dropna().unique().tolist()

        logger.info(f"📊 Loaded F&O Symbols: {len(symbols)}")
        return symbols

    except Exception as e:
        logger.error(f"❌ CSV Load Error: {e}")
        return []


# ---------------- MAIN SCANNER ----------------

def run_full_scan():

    fetcher = DataFetcher()
    detector = PatternDetector()
    telegram = TelegramPoster()

    symbols = load_fno_symbols()

    if not symbols:
        logger.error("❌ No symbols loaded. Scanner stopped.")
        return []

    results = []
    scanned = 0
    signals = 0

    logger.info("🚀 STARTING FULL F&O MARKET SCAN")

    for symbol in symbols:

        try:
            scanned += 1
            logger.info(f"🔍 Scanning: {symbol}")

            data = fetcher.get_stock_data(symbol)

            if data is None or data.empty:
                logger.warning(f"⚠ No data: {symbol}")
                continue

            result = detector.analyze(symbol, data)

            if result and result.get("has_pattern"):

                signals += 1

                output = {
                    "symbol": symbol,
                    "trend": result.get("trend"),
                    "signal": result.get("signal"),
                }

                results.append(output)

                logger.info(f"🔥 SIGNAL: {symbol} | {output['signal']}")

            # prevent API overload
            time.sleep(0.2)

        except Exception as e:
            logger.error(f"{symbol} error: {e}")

    # ---------------- SUMMARY ----------------

    logger.info("📊 FULL SCAN COMPLETE")
    logger.info(f"Total Scanned: {scanned}")
    logger.info(f"Signals Found: {signals}")

    # ---------------- TELEGRAM OUTPUT ----------------

    try:
        if results:

            message = "🔥 TOP MARKET SETUPS\n\n"

            for t in results[:10]:
                message += f"{t['symbol']} | {t['signal']} | {t['trend']}\n"

            telegram.send_message("free", message)

        else:
            telegram.send_message(
                "free",
                "⚠ No strong setups found in current market conditions."
            )

    except Exception as e:
        logger.error(f"❌ Telegram send failed: {e}")

    return results
