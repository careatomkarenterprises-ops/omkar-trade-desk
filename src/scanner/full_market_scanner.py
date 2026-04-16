import pandas as pd
import time
import logging

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(**name**)

def load_fno_symbols():
try:
df = pd.read_csv("fno_stocks.csv")
symbols = df["symbol"].dropna().unique().tolist()

```
    logger.info(f"📊 Loaded F&O Symbols: {len(symbols)}")
    return symbols

except Exception as e:
    logger.error(f"❌ CSV Load Error: {e}")
    return []
```

def run_full_scan():

```
fetcher = DataFetcher()
detector = PatternDetector()
telegram = TelegramPoster()

symbols = load_fno_symbols()

if not symbols:
    logger.error("❌ No symbols loaded. Stopping scan.")
    return []

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

            logger.info(f"🔥 SIGNAL: {symbol} | {result.get('signal')}")

        time.sleep(0.2)

    except Exception as e:
        logger.error(f"{symbol} error: {e}")

# ---------------- SUMMARY ----------------

logger.info("📊 FULL SCAN COMPLETE")
logger.info(f"Total Scanned: {scanned}")
logger.info(f"Signals Found: {signals}")

# ---------------- NO SIGNAL CASE ----------------

if not results:
    try:
        telegram.send_message(
            "free",
            "⚠ No strong setups found in current market conditions."
        )
    except Exception as e:
        logger.error(f"Telegram error: {e}")

    return []

# ---------------- SORT (IMPORTANT) ----------------

# Currently no strength score, so just limit to first 10
top = results[:10]

# ---------------- PREMIUM MESSAGE ----------------

premium_msg = "🔥 PREMIUM TRADE SETUPS\n\n"

for t in top:
    premium_msg += f"{t['symbol']} | {t['signal']} | {t['trend']}\n"

# ---------------- FREE MESSAGE (DELAY STYLE) ----------------

free_msg = "📊 MARKET INSIGHT (EDUCATIONAL)\n\n"

for t in top[:3]:
    free_msg += f"{t['symbol']} showing {t['trend']} structure\n"

free_msg += "\n⚠ For real-time signals → Join Premium"

# ---------------- TELEGRAM SEND ----------------

try:
    telegram.send_message("premium", premium_msg)
    telegram.send_message("free", free_msg)

    logger.info("✅ Telegram messages sent successfully")

except Exception as e:
    logger.error(f"❌ Telegram send failed: {e}")

return results
```
