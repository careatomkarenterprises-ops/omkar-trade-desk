import logging
from src.scanner.zerodha_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.scanner.premarket_engine import PreMarketPredictionEngine
from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
from src.telegram.poster import TelegramPoster
# Assuming these are the names of your agent classes
from src.agents.currency_agent import CurrencyAgent 
from src.agents.commodity_agent import CommodityAgent

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.premarket = PreMarketPredictionEngine(self.fetcher, self.detector)
        self.global_engine = GlobalMarketEngine()
        self.options_engine = OptionsIntelligenceEngine()
        self.telegram = TelegramPoster()

    def run_premarket(self):
        try:
            global_data = self.global_engine.run()
            self.premarket.run(global_data=global_data)
        except Exception as e:
            logger.error(f"Premarket failure: {e}")

    def run_live_session(self):
        # 1. Global Update
        global_data = self.global_engine.run()
        
        # 2. Options Update
        self.options_engine.run()

        # 3. Currency - FIX: No arguments passed
        try:
            CurrencyAgent().scan() 
        except Exception as e:
            logger.error(f"❌ Currency Failed: {e}")

        # 4. Commodity - FIX: No arguments passed
        try:
            CommodityAgent().scan()
        except Exception as e:
            logger.error(f"❌ Commodity Failed: {e}")

        logger.info("✅ Live Session Cycle Complete")
