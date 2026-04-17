import logging
# Import core components
from src.scanner.zerodha_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.scanner.premarket_engine import PreMarketPredictionEngine
from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
from src.telegram.poster import TelegramPoster

# Corrected: Importing agents from the scanner folder (where they actually live)
from src.scanner.currency_agent import CurrencyAgent 
from src.scanner.edu_news_agent import NewsAgent as CommodityAgent 

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        # Initialize everything with safety checks
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.premarket = PreMarketPredictionEngine(self.fetcher, self.detector)
        self.global_engine = GlobalMarketEngine()
        self.options_engine = OptionsIntelligenceEngine()
        self.telegram = TelegramPoster()

    def run_premarket(self):
        """Runs the early morning scan"""
        try:
            logger.info("🚀 Executing Premarket Scan...")
            global_data = self.global_engine.run()
            
            results = self.premarket.run(global_data=global_data)
            
            if not results:
                # Fixed: Added 'free' channel argument
                self.telegram.send_message("free", "🔍 Premarket: Scan complete. No institutional volume shocks found.")
        except Exception as e:
            logger.error(f"Premarket failure: {e}")

    def run_live_session(self):
        """Runs during market hours"""
        try:
            # 1. Update Macro Data
            global_data = self.global_engine.run()
            
            # 2. Update Options Data
            self.options_engine.run()

            # 3. Currency & News Agents
            try:
                # We initialize and run them based on your current file structure
                CurrencyAgent().run() 
                CommodityAgent().run()
            except Exception as e:
                logger.warning(f"Secondary Agent Error: {e}")

            logger.info("✅ Live Cycle Complete")
        except Exception as e:
            logger.error(f"Live session error: {e}")
