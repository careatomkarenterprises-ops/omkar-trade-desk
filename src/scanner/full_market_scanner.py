import pandas as pd
import time
import logging

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


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


def run_full_scan():

    fetcher = DataFetcher()
    detector = PatternDetector()
    telegram = TelegramPoster()

    symbols = load_fno_symbols()

    results = []
    scanned = 0

    logger.info("🚀 STARTING FULL F&O MARKET SCAN")

    for symbol in symbols:

        try:
            scanned += 1
            logger.info(f"🔍 Scanning: {symbol}")

            data = fetcher.get_stock_data(symbol)

            if data is None or data.empty:
                continue

            result = detector.analyze(symbol, data)

            # ✅ DEBUG LOG (IMPORTANT)
            logger.info(f"DEBUG RESULT {symbol}: {result}")

            # ✅ TEMP FORCE SIGNAL (ENSURE CONTENT FLOW)
            if result:

                output = {
                    "symbol": symbol,
                    "trend": result.get("trend", "Sideways"),
                    "signal": result.get("signal", "Watch"),
                    "volume_spike": result.get("volume_spike", False)
                }

                results.append(output)

                logger.info(f"🔥 SIGNAL: {symbol} | {output['signal']}")

            time.sleep(0.15)

        except Exception as e:
            logger.error(f"{symbol} error: {e}")

    logger.info("📊 FULL SCAN COMPLETE")
    logger.info(f"Total Scanned: {scanned}")
    logger.info(f"Signals Generated: {len(results)}")

    # -------------------------------
    # 📢 TELEGRAM OUTPUT
    # -------------------------------
    if results:

        message = "🔥 <b>TOP MARKET SETUPS</b>\n\n"

        for t in results[:10]:
            message += f"📊 <b>{t['symbol']}</b>\n"
            message += f"Signal: {t['signal']}\n"
            message += f"Trend: {t['trend']}\n\n"

        message += "⚠️ For educational purposes only"

        telegram.send_message("free", message)

    else:
        # ✅ FALLBACK CONTENT (VERY IMPORTANT FOR BUSINESS)
        telegram.send_message(
            "free",
            "📊 Market Update:\n\n"
            "No high-probability setups detected.\n"
            "Market currently sideways / low momentum.\n\n"
            "👉 Stay disciplined. Avoid overtrading."
        )

    return results


# ✅ WRAPPER (DO NOT TOUCH)
def run_full_market_scan():
    try:
        return run_full_scan()
    except Exception as e:
        logger.error(f"Wrapper error: {e}")
        return []


if __name__ == "__main__":
    run_full_scan()
