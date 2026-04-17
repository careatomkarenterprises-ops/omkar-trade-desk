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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemController:

    def __init__(self):
        self.global_engine = GlobalMarketEngine()

    def run(self):

        now = datetime.datetime.now()

        logger.info(f"🚀 SYSTEM START | TIME: {now}")

        # 🌍 GLOBAL MARKET
        global_data = self.global_engine.run()
        logger.info(f"🌍 GLOBAL BIAS: {global_data.get('overall_bias')}")

        # 🌅 PREMARKET
        if now.hour < 9:

            logger.info("🔥 PREMARKET MODE")
            PreMarketPredictionEngine().run()

        # 📊 LIVE MARKET
        elif 9 <= now.hour < 16:

            logger.info("📊 LIVE MARKET MODE")

            # 🔥 MAIN SCANNER (YOUR CORE LOGIC)
            results = run_full_scan()

            logger.info(f"🔥 Signals Found: {len(results)}")

            # 📊 OPTIONS
            OptionsIntelligenceEngine().run()

            # 💱 CURRENCY
            CurrencyAgent().run()

            # 🛢️ COMMODITY
            CommodityAgent().run()

        # 🌙 EOD
        else:

            logger.info("📉 EOD MODE")

            EODEngine().run(global_data)
            LearningEngine().run(global_data)

        logger.info("✅ SYSTEM COMPLETE")
