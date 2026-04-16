import datetime
import logging

from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.premarket_engine import PreMarketPredictionEngine
from src.scanner.eod_engine import EODEngine
from src.scanner.learning_engine import LearningEngine

# ✅ NEW IMPORT (IMPORTANT)

from src.scanner.full_market_scanner import run_full_scan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

class SystemController:

```
def __init__(self):
    self.global_engine = GlobalMarketEngine()

def run(self):

    now = datetime.datetime.now()

    logger.info(f"🚀 SYSTEM START | TIME: {now}")

    # ---------------- GLOBAL MARKET ----------------
    global_data = self.global_engine.run()
    logger.info(f"🌍 GLOBAL BIAS: {global_data.get('overall_bias')}")

    # ---------------- PRE-MARKET ----------------
    if now.hour < 9:

        logger.info("🔥 PREMARKET ENGINE START")

        engine = PreMarketPredictionEngine()
        engine.run()

    # ---------------- MARKET HOURS ----------------
    elif 9 <= now.hour < 16:

        logger.info("📊 MARKET LIVE MODE")

        # ✅ FULL SCANNER (YOUR LOCAL LOGIC CONNECTED)
        run_full_scan()

    # ---------------- EOD ----------------
    else:

        logger.info("📉 EOD ENGINE START")

        EODEngine().run(global_data)
        LearningEngine().run(global_data)

    logger.info("✅ SYSTEM COMPLETE")
```

def main():
SystemController().run()
