import pandas as pd
import time
import json
import logging

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


# ================================
# 📊 LOAD SYMBOLS
# ================================
def load_fno_symbols():
    try:
        df = pd.read_csv("fno_stocks.csv")

        if "symbol" in df.columns:
            symbols = df["symbol"].dropna().unique().tolist()
        else:
            symbols = df.iloc[:, 0].dropna().unique().tolist()

        logger.info(f"📊 Loaded F&O Symbols: {len(symbols)}")
        return symbols

    except Exception as e:
        logger.error(f"❌ CSV Load Error: {e}")
        return ["RELIANCE", "TCS", "INFY", "HDFCBANK"]


# ================================
# 🚀 MAIN SCANNER
# ================================
def run_full_scan():

    fetcher = DataFetcher()
    detector = PatternDetector()
    telegram = TelegramPoster()

    symbols = load_fno_symbols()

    results = []
    scanned = 0
    signals = 0

    logger.info("🚀 STARTING FULL MARKET SCAN")

    for symbol in symbols:

        try:
            scanned += 1
            logger.info(f"🔍 Scanning: {symbol}")

            data = fetcher.get_stock_data(symbol)

            if data is None or data.empty:
                continue

            # ================================
            # 🔥 YOUR REAL STRATEGY (IMPORTANT)
            # ================================
            result = detector.analyze(symbol, data)

            if result and result.get("has_pattern"):

                signals += 1

                output = {
                    "symbol": symbol,
                    "signal": result.get("trigger"),
                    "price": result.get("price"),
                    "strength": round(result.get("strength", 0), 2),
                    "surge": result.get("surge_ratio"),
                    "type": result.get("pattern_type", "SMART_SETUP")
                }

                results.append(output)

                logger.info(f"🔥 SIGNAL: {symbol} | Score: {output['strength']}")

            time.sleep(0.2)

        except Exception as e:
            logger.error(f"{symbol} error: {e}")

    # ================================
    # 📊 SUMMARY
    # ================================
    logger.info("📊 FULL SCAN COMPLETE")
    logger.info(f"Total Scanned: {scanned}")
    logger.info(f"Signals Found: {signals}")

    # ================================
    # 💾 SAVE RESULTS
    # ================================
    try:
        with open("data/full_fno_scan_results.json", "w") as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.error(f"Save error: {e}")

    # ================================
    # 📢 TELEGRAM OUTPUT
    # ================================
    if results:

        # sort by strength
        top = sorted(results, key=lambda x: x["strength"], reverse=True)[:10]

        message = "🔥 <b>SMART MONEY SETUPS</b>\n\n"

        for t in top:
            message += f"📊 <b>{t['symbol']}</b>\n"
            message += f"Signal: {t['signal']}\n"
            message += f"Strength: {t['strength']}\n"
            message += f"Price: {t['price']}\n"
            message += f"Volume Surge: {t['surge']}\n\n"

        message += "⚠️ Ranked by Strength Engine"

        telegram.send_message("free", message)

    else:
        telegram.send_message(
            "free",
            "📊 Market Update:\n\n"
            "No strong setups found.\n"
            "Market in compression.\n\n"
            "👉 Smart money waiting."
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
