import datetime
import logging
import json
import os
from datetime import datetime
import pytz

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
from src.telegram.poster import TelegramPoster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketIntelligenceOrchestrator:

    def __init__(self):

        logger.info("🚀 Initializing Hedge Fund Intelligence System")

        self.fetcher = DataFetcher()
        self.pattern = PatternDetector()
        self.options = OptionsIntelligenceEngine()
        self.poster = TelegramPoster()
        self.global_engine = GlobalMarketEngine()

        self.output_file = "data/final_signals.json"
        os.makedirs("data", exist_ok=True)

    # ----------------------------
    # RANKING ENGINE (IMPORTANT)
    # ----------------------------
    def rank_signals(self, signals):

        ranked = sorted(
            signals,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        return ranked[:5]  # TOP 5 ONLY (HEDGE FUND STYLE)

    # ----------------------------
    # MAIN SCAN ENGINE
    # ----------------------------
    def run(self):

        if not self.fetcher.is_ready():
            logger.error("Market Data Not Ready")
            return

        now = datetime.now()
        logger.info(f"🕒 Running Cycle at {now}")

        # 🌍 GLOBAL CONTEXT
        global_data = self.global_engine.run()

        symbols = self.fetcher.get_fno_symbols()

        signals = []

        for symbol in symbols:

            try:
                data = self.fetcher.get_stock_data(symbol)

                if data is None or data.empty:
                    continue

                # -------------------------
                # 1. PATTERN DETECTION
                # -------------------------
                pattern_result = self.pattern.analyze(symbol, data)

                if not pattern_result or not pattern_result.get("has_pattern"):
                    continue

                # -------------------------
                # 2. OPTIONS INTELLIGENCE
                # -------------------------
                spot = data["close"].iloc[-1]

                options_signal = self.options.generate_options_signal(
                    nifty_data=data,
                    banknifty_data=data
                )

                # -------------------------
                # 3. SCORE ENGINE
                # -------------------------
                score = 0

                score += pattern_result.get("strength", 0) * 40
                score += options_signal.get("confidence", 0) * 0.6

                final_signal = {
                    "symbol": symbol,
                    "price": spot,
                    "pattern": pattern_result.get("trigger"),
                    "support": pattern_result.get("support"),
                    "resistance": pattern_result.get("resistance"),
                    "volume_surge": pattern_result.get("surge_ratio"),
                    "options_bias": options_signal.get("bias", {}).get("overall_bias"),
                    "strike_plan": options_signal.get("strike_plan"),
                    "confidence": round(score, 2)
                }

                signals.append(final_signal)

            except Exception as e:
                logger.error(f"Error in {symbol}: {e}")

        # ----------------------------
        # RANK TOP SETUPS
        # ----------------------------
        top_signals = self.rank_signals(signals)

        # ----------------------------
        # SAVE OUTPUT
        # ----------------------------
        with open(self.output_file, "w") as f:
            json.dump(top_signals, f, indent=2)

        # ----------------------------
        # TELEGRAM REPORT
        # ----------------------------
        self.send_report(top_signals)

        logger.info(f"✅ Cycle Complete | Signals: {len(top_signals)}")

    # ----------------------------
    # TELEGRAM REPORT ENGINE
    # ----------------------------
    def send_report(self, signals):

        if not signals:
            self.poster.send_message("free",
                "📊 Market Scan Complete\n\nNo high-probability setups found today.")
            return

        message = "🚀 HEDGE FUND INTELLIGENCE REPORT\n\n"

        for s in signals:

            message += (
                f"📌 {s['symbol']}\n"
                f"💰 Price: {s['price']}\n"
                f"📊 Pattern: {s['pattern']}\n"
                f"📈 Confidence: {s['confidence']}/100\n"
                f"📦 Range: {s['support']} - {s['resistance']}\n"
                f"⚡ Options Bias: {s['options_bias']}\n\n"
            )

        self.poster.send_message("free", message)


# ----------------------------
# ENTRY POINT
# ----------------------------
def main():

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    # 🚫 WEEKEND FILTER
    if now.weekday() >= 5:
        logger.info("Weekend - No Market")
        return

    engine = MarketIntelligenceOrchestrator()
    engine.run()


if __name__ == "__main__":
    main()
