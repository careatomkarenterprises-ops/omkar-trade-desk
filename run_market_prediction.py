import logging
from datetime import datetime

from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.premarket_engine import PreMarketEngine
from src.telegram.telegram_report_engine import TelegramReportEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafePreMarketPredictor:

    def __init__(self):
        self.global_engine = GlobalMarketEngine()
        self.premarket_engine = PreMarketEngine()
        self.telegram = TelegramReportEngine()

    # ============================
    # SIMPLE MARKET CONTEXT LAYER
    # ============================
    def derive_market_context(self, global_data):
        try:
            bias = global_data.get("overall_bias", "NEUTRAL")
            volatility = global_data.get("volatility", "NORMAL")

            if bias == "BULLISH" and volatility == "HIGH":
                state = "TRENDING BULLISH + VOLATILE"
            elif bias == "BEARISH" and volatility == "HIGH":
                state = "TRENDING BEARISH + VOLATILE"
            elif bias == "BULLISH":
                state = "POSITIVE OPEN EXPECTED"
            elif bias == "BEARISH":
                state = "NEGATIVE OPEN EXPECTED"
            else:
                state = "SIDEWAYS / RANGE BOUND"

            return {
                "bias": bias,
                "volatility": volatility,
                "state": state
            }

        except Exception as e:
            logger.error(f"Context error: {e}")
            return {
                "bias": "NEUTRAL",
                "volatility": "NORMAL",
                "state": "UNCERTAIN"
            }

    # ============================
    # RUN ENGINE
    # ============================
    def run(self):

        try:
            logger.info("🚀 SAFE PRE-MARKET ENGINE STARTED")

            # STEP 1: GLOBAL MARKET CONTEXT (yfinance handled inside engine)
            global_data = self.global_engine.run()

            # STEP 2: DERIVE SIMPLE CONTEXT LAYER (NO RISK LOGIC)
            context = self.derive_market_context(global_data)

            # STEP 3: PRE-MARKET SETUPS (your existing smart money / scanner logic)
            setups = self.premarket_engine.run(global_data)

            # STEP 4: SAFETY CHECK
            if setups is None:
                setups = []

            # STEP 5: ENRICH DATA (SAFE ADDITION ONLY)
            enriched_data = {
                "context": context,
                "setups": setups,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }

            # STEP 6: SEND TO TELEGRAM
            self.telegram.send_premarket_report(setups, global_data)

            logger.info("✅ PRE-MARKET REPORT SENT SUCCESSFULLY")

        except Exception as e:
            logger.error(f"❌ PreMarket Predictor Error: {e}")

            # SAFE FALLBACK (NEVER BREAK PIPELINE)
            self.telegram.send_message(
                "⚠️ Pre-Market Engine temporarily unavailable.\n"
                "System will retry in next scheduled run."
            )


# ============================
# ENTRY POINT
# ============================
if __name__ == "__main__":
    SafePreMarketPredictor().run()
