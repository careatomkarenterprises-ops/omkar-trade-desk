import logging
import sys
import traceback

# Core Engine Imports
try:
    from src.scanner.zerodha_fetcher import DataFetcher
    from src.scanner.patterns import PatternDetector
    from src.scanner.premarket_engine import PreMarketPredictionEngine
    from src.scanner.global_market_engine import GlobalMarketEngine
    from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
    from src.telegram.poster import TelegramPoster
except ImportError as e:
    print(f"DEBUGGER: Core Import Error: {e}")
    print(traceback.format_exc())

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        logger.info("🛠️ Initializing System Controller...")
        try:
            self.fetcher = DataFetcher()
            self.detector = PatternDetector()
            self.premarket = PreMarketPredictionEngine(self.fetcher, self.detector)
            self.global_engine = GlobalMarketEngine()
            self.options_engine = OptionsIntelligenceEngine()
            self.telegram = TelegramPoster()
            
            # Setup Agents as None initially
            self.currency_agent = None
            self.news_agent = None
            self._load_agents_with_debug()
            
        except Exception as e:
            logger.error(f"💥 Controller Init Failed: {e}")
            print(traceback.format_exc())

    def _load_agents_with_debug(self):
        """Advanced Debugger for loading secondary agents"""
        # Try Currency Agent
        try:
            from src.scanner.currency_agent import CurrencyAgent
            self.currency_agent = CurrencyAgent()
            logger.info("✅ Currency Agent Loaded")
        except Exception as e:
            logger.warning(f"⚠️ DEBUGGER: CurrencyAgent load failed: {e}")

        # Try News/Edu Agent
        try:
            # We try multiple common class names to find yours
            import src.scanner.edu_news_agent as news_mod
            # List all classes in the file to find the right one
            classes = [cls for cls in dir(news_mod) if not cls.startswith('_')]
            logger.info(f"DEBUGGER: Found classes in edu_news_agent: {classes}")
            
            if 'EduNewsAgent' in classes:
                self.news_agent = news_mod.EduNewsAgent()
            elif 'NewsAgent' in classes:
                self.news_agent = news_mod.NewsAgent()
            elif 'Agent' in classes:
                self.news_agent = news_mod.Agent()
            
            if self.news_agent:
                logger.info("✅ News Agent Loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ DEBUGGER: NewsAgent load failed: {e}")

    def run_live_session(self):
        """Main execution loop with diagnostic checkpoints"""
        try:
            logger.info("🚀 Starting Live Intelligence Cycle")
            
            # Checkpoint 1: Global Market Engine
            logger.info("Checkpoint 1: Global Macro...")
            global_data = self.global_engine.run()
            
            # Checkpoint 2: Options Engine
            logger.info("Checkpoint 2: Options Intelligence...")
            self.options_engine.run()

            # Checkpoint 3: Secondary Agents
            if self.currency_agent:
                logger.info("Checkpoint 3a: Running Currency Scan...")
                try: self.currency_agent.run() 
                except Exception as e: logger.error(f"Currency Run Error: {e}")
            
            if self.news_agent:
                logger.info("Checkpoint 3b: Running News/Edu Scan...")
                try: self.news_agent.run()
                except Exception as e: logger.error(f"News Run Error: {e}")

            logger.info("✅ Live Cycle Complete")
            
        except Exception as e:
            logger.error(f"❌ System Controller Live Session Error: {e}")
            print(traceback.format_exc())
