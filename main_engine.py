import logging
from datetime import datetime

from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.premarket_engine import PreMarketEngine
from src.scanner.core import OmkarTradeDesk
from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
from src.scanner.eod_engine import EODEngine
from src.scanner.learning_engine import LearningEngine
from src.scanner.data_fetcher import DataFetcher
from src.telegram.telegram_report_engine import TelegramReportEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterEngine:

    def __init__(self):

        logger.info("🚀 INITIALIZING HEDGE FUND INTELLIGENCE SYSTEM")

        self.global_engine = GlobalMarketEngine()
        self.fetcher = DataFetcher()
        self.telegram = TelegramReportEngine()

    def run(self):

        now = datetime.now()

        # ---------------- GLOBAL CONTEXT ----------------
        global_data = self.global_engine.run()

        logger.info(f"🌍 Market Bias: {global_data.get('overall_bias')}")

        # ---------------- OPTIONS ENGINE ----------------
        try:
            options_engine = OptionsIntelligenceEngine()

            nifty = self.fetcher.get_stock_data("NIFTY 50")
            banknifty = self.fetcher.get_stock_data("BANKNIFTY")

            options_signal = options_engine.generate_options_signal(
                nifty, banknifty
            )

            logger.info(f"📊 Options Flow: {options_signal}")

        except Exception as e:
            logger.error(f"Options Engine Error: {e}")

        # ---------------- SESSION BASED LOGIC ----------------

        if now.hour < 9:

            logger.info("🚀 PREMARKET SESSION")

            engine = PreMarketEngine()
            setups = engine.run(global_data)

            self.telegram.send_premarket_report(setups, global_data)

        elif 9 <= now.hour < 16:

            logger.info("📊 LIVE MARKET MODE")

            scanner = OmkarTradeDesk()
            scanner.execute_scan()

        else:

            logger.info("📉 EOD SESSION")

            eod = EODEngine()
            eod.run(global_data)

            learning = LearningEngine()
            learning.run(global_data)

            self.telegram.send_eod_report(global_data)


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    MasterEngine().run()
