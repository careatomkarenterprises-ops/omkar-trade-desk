import datetime
import logging

from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.premarket_engine import PreMarketPredictionEngine
from src.scanner.eod_engine import EODEngine
from src.scanner.learning_engine import LearningEngine
from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
from src.scanner.full_market_scanner import run_full_scan
from src.scanner.currency_agent import CurrencyAgent
from src.scanner.commodity_agent import CommodityAgent
from src.telegram.poster import TelegramPoster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemController:

    def __init__(self):
        self.global_engine = GlobalMarketEngine()
        self.telegram = TelegramPoster()

    def run(self):

        now = datetime.datetime.now()

        logger.info("🔥 CONTROLLER RUNNING")
        logger.info(f"🕒 TIME: {now}")

        # 🌍 GLOBAL MARKET
        global_data = self.global_engine.run()

        global_msg = f"""
🌍 GLOBAL MARKET UPDATE

Bias: {global_data.get('overall_bias')}
USDINR: {global_data.get('currency', {}).get('usd_inr')}
Crude: {global_data.get('crude_oil', {}).get('trend')}
        """

        self.telegram.send_message("free", global_msg)

        # 🌅 PREMARKET
        if now.hour < 9:

            logger.info("🔥 PREMARKET MODE")

            PreMarketPredictionEngine().run()

        # 📊 LIVE MARKET
        elif 9 <= now.hour < 16:

            logger.info("📊 LIVE MARKET MODE")

            # 🔥 MAIN SCANNER
            results = run_full_scan()

            if results:
                msg = "🔥 LIVE MARKET SIGNALS\n\n"
                for r in results[:10]:
                    msg += f"{r['symbol']} | {r['signal']} | {r['trend']}\n"

                self.telegram.send_message("free", msg)

            # 📈 OPTIONS
            opt = OptionsIntelligenceEngine().run()

            self.telegram.send_message(
                "free",
                f"📊 OPTIONS UPDATE\nBias: {opt.get('flow', {}).get('signal')}"
            )

            # 💱 CURRENCY
            CurrencyAgent().run()
            self.telegram.send_message("free", "💱 Currency Engine Updated")

            # 🛢️ COMMODITY
            CommodityAgent().run()
            self.telegram.send_message("free", "🛢️ Commodity Engine Updated")

        # 🌙 EOD
        else:

            logger.info("📉 EOD MODE")

            EODEngine().run(global_data)
            LearningEngine().run(global_data)

            self.telegram.send_message(
                "free",
                "📉 End of Day Analysis Completed"
            )

        logger.info("✅ SYSTEM COMPLETE")


def main():
    SystemController().run()
