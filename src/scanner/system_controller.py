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
            
            # Setup Agents
            self.currency_agent = None
            self.news_agent = None
            self._load_agents_with_debug()
            
        except Exception as e:
            logger.error(f"💥 Controller Init Failed: {e}")

    def _load_agents_with_debug(self):
        """Fixed: Passing 'kite' instance to agents that require it"""
        # 1. Load Currency Agent
        try:
            from src.scanner.currency_agent import CurrencyAgent
            self.currency_agent = CurrencyAgent()
            logger.info("✅ Currency Agent Loaded")
        except Exception as e:
            logger.warning(f"⚠️ CurrencyAgent load failed: {e}")

        # 2. Load News/Edu Agent (Fixed positional argument 'kite')
        try:
            import src.scanner.edu_news_agent as news_mod
            # We pass self.fetcher.kite because the logs say it's required
            if hasattr(news_mod, 'EduNewsAgent'):
                self.news_agent = news_mod.EduNewsAgent(kite=self.fetcher.kite)
                logger.info("✅ EduNewsAgent Loaded with Kite context")
            elif hasattr(news_mod, 'NewsAgent'):
                self.news_agent = news_mod.NewsAgent(kite=self.fetcher.kite)
                logger.info("✅ NewsAgent Loaded with Kite context")
        except Exception as e:
            logger.warning(f"⚠️ NewsAgent load failed: {e}")

    def run(self):
        """
        Fixed: Renamed from run_live_session to 'run' 
        to match your execution_layer.py call.
        """
        try:
            logger.info("🚀 Starting Omkar Trade Desk Execution...")
            
            # Step 1: Global Macro & Options
            logger.info("📊 Processing Global Markets & Options...")
            global_data = self.global_engine.run()
            self.options_engine.run()

            # Step 2: Currency Scan
            if self.currency_agent:
                try:
                    logger.info("💱 Running Currency Agent...")
                    # Try common run methods
                    if hasattr(self.currency_agent, 'run'): self.currency_agent.run()
                    elif hasattr(self.currency_agent, 'scan'): self.currency_agent.scan()
                except Exception as e:
                    logger.error(f"Currency Agent Execution Error: {e}")
            
            # Step 3: News/Edu Scan
            if self.news_agent:
                try:
                    logger.info("📰 Running News Intelligence Agent...")
                    if hasattr(self.news_agent, 'run'): self.news_agent.run()
                    elif hasattr(self.news_agent, 'scan'): self.news_agent.scan()
                except Exception as e:
                    logger.error(f"News Agent Execution Error: {e}")

            logger.info("✅ ALL SCANS COMPLETE")
            
        except Exception as e:
            logger.error(f"❌ System Controller Run Error: {e}")
            print(traceback.format_exc())

    def run_live_session(self):
        """Alias for compatibility"""
        self.run()
