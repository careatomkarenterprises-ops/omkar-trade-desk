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
from src.scanner.morning_setup import get_kite_instance
from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemController:

    def __init__(self):
        self.global_engine = GlobalMarketEngine()
        self.telegram = TelegramPoster()

        # ✅ CORE DEPENDENCIES
        self.kite = get_kite_instance()
        self.data_fetcher = DataFetcher()
        self.pattern_detector = PatternDetector()

        if not self.kite:
            logger.warning("⚠ Kite instance NOT initialized")

    def run(self):

        now = datetime.datetime.now()

        logger.info("🔥 CONTROLLER RUNNING")
        logger.info(f"🕒 TIME: {now}")

        # 🌍 GLOBAL MARKET
        try:
            global_data = self.global_engine.run()

            if not global_data:
                global_data = {}

            msg = f"""
🌍 GLOBAL MARKET UPDATE

Bias: {global_data.get('overall_bias')}
USDINR: {global_data.get('currency', {}).get('usd_inr')}
Crude: {global_data.get('crude_oil', {}).get('trend')}
            """

            self.telegram.send_message("free", msg)

        except Exception as e:
            logger.error(f"❌ Global Engine Failed: {e}")
            global_data = {}

        # 🌅 PREMARKET (Before 9:15 AM)
        if now.hour < 9 or (now.hour == 9 and now.minute < 15):

            logger.info("🔥 PREMARKET MODE")

            try:
                engine = PreMarketPredictionEngine(
                    self.data_fetcher,
                    self.pattern_detector
                )

                # ✅ CORRECT FIX
                engine.run([], global_data)

                logger.info("✅ Premarket Completed")

            except Exception as e:
                logger.error(f"❌ Premarket Failed: {e}")

        # 📊 LIVE MARKET
        elif 9 <= now.hour < 16:

            logger.info("📊 LIVE MARKET MODE")

            # 🔥 SCANNER
            try:
                results = run_full_scan()

                if results:
                    msg = "🔥 LIVE MARKET SIGNALS\n\n"
                    for r in results[:10]:
                        msg += f"{r['symbol']} | {r['signal']} | {r['trend']}\n"

                    self.telegram.send_message("free", msg)

            except Exception as e:
                logger.error(f"❌ Scanner Failed: {e}")

            # 📈 OPTIONS
            try:
                opt = OptionsIntelligenceEngine().run()

                self.telegram.send_message(
                    "free",
                    f"📊 OPTIONS UPDATE\n{opt}"
                )

            except Exception as e:
                logger.error(f"❌ Options Failed: {e}")

            # 💱 CURRENCY (DO NOT CHANGE)
            try:
                if self.kite:
                    CurrencyAgent(self.kite).scan()
                    self.telegram.send_message("free", "💱 Currency Done")
                else:
                    logger.warning("⚠ Currency Skipped - No Kite")

            except Exception as e:
                logger.error(f"❌ Currency Failed: {e}")

            # 🛢️ COMMODITY (DO NOT CHANGE)
            try:
                if self.kite:
                    CommodityAgent(self.kite).scan()
                    self.telegram.send_message("free", "🛢️ Commodity Done")
                else:
                    logger.warning("⚠ Commodity Skipped - No Kite")

            except Exception as e:
                logger.error(f"❌ Commodity Failed: {e}")

        # 🌙 EOD
        else:

            logger.info("📉 EOD MODE")

            try:
                EODEngine().run(global_data)
                LearningEngine().run(global_data)

                self.telegram.send_message(
                    "free",
                    "📉 End of Day Completed"
                )

            except Exception as e:
                logger.error(f"❌ EOD Failed: {e}")

        logger.info("✅ SYSTEM COMPLETE")


def main():
    SystemController().run()
