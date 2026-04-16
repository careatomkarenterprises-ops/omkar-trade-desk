import pandas as pd
import time
import json
import logging

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


def load_fno_symbols():
    try:
        df = pd.read_csv("fno_stocks.csv")
        symbols = df["symbol"].dropna().unique().tolist()

        logger.info(f"📊 Loaded F&O Symbols: {len(symbols)}")
        return symbols

    except Exception as e:
        logger.error(f"❌ CSV Load Error: {e}")
        return []


def run_full_scan():

    fetcher = DataFetcher()
    detector = PatternDetector()
    telegram = TelegramPoster()

    symbols = load_fno_symbols()

    results = []
    scanned = 0
    signals = 0

    logger.info("🚀 STARTING FULL F&O MARKET SCAN")

    for symbol in symbols:

        try:
            scanned += 1

            data = fetcher.get_stock_data(symbol)

            if data is None or data.empty:
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

                logger.info(f"🔥 SIGNAL: {symbol}")

            time.sleep(0.2)

        except Exception as e:
            logger.error(f"{symbol} error: {e}")

    # ---------------- SUMMARY ----------------

    logger.info("📊 FULL SCAN COMPLETE")
    logger.info(f"Total Scanned: {scanned}")
    logger.info(f"Signals Found: {signals}")

    # ---------------- TOP SIGNALS ----------------

    if results:

        top = results[:10]

        message = "🔥 TOP MARKET SETUPS\n\n"

        for t in top:
            message += f"{t['symbol']} | {t['signal']} | {t['trend']}\n"

        # ✅ SEND TELEGRAM
        telegram.send_message("free", message)

    else:
        telegram.send_message(
            "free",
            "⚠ No strong setups found in current market conditions."
        )

    return results
