import logging
import traceback

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        logger.info("🛠️ Initializing Omkar System Controller...")
        try:
            # Import inside init to avoid circular dependency
            from src.scanner.zerodha_fetcher import DataFetcher
            from src.scanner.patterns import PatternDetector
            from src.scanner.global_market_engine import GlobalMarketEngine
            from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
            from src.telegram.poster import TelegramPoster
            
            self.fetcher = DataFetcher()
            self.detector = PatternDetector()
            self.global_engine = GlobalMarketEngine()
            self.options_engine = OptionsIntelligenceEngine()
            self.telegram = TelegramPoster()
            
            # Setup Agents
            self.currency_agent = None
            self.news_agent = None
            self._load_agents_with_context()
            
        except Exception as e:
            logger.error(f"💥 Controller Init Failed: {e}")

    def _load_agents_with_context(self):
        """Fixed: Ensuring BOTH agents receive the Kite connection"""
        # 1. Load Currency Agent
        try:
            from src.scanner.currency_agent import CurrencyAgent
            self.currency_agent = CurrencyAgent()
            # INJECTION: Pass the kite instance directly to fix 'Kite not available'
            if hasattr(self.currency_agent, 'kite'):
                self.currency_agent.kite = self.fetcher.kite
            logger.info("✅ Currency Agent Loaded & Kite Injected")
        except Exception as e:
            logger.warning(f"⚠️ CurrencyAgent load failed: {e}")

        # 2. Load News/Edu Agent
        try:
            import src.scanner.edu_news_agent as news_mod
            if hasattr(news_mod, 'EduNewsAgent'):
                self.news_agent = news_mod.EduNewsAgent(kite=self.fetcher.kite)
                logger.info("✅ EduNewsAgent Loaded")
        except Exception as e:
            logger.warning(f"⚠️ NewsAgent load failed: {e}")

    def run(self):
        """Main execution method"""
        try:
            logger.info("🚀 OMKAR INTELLIGENCE CYCLE STARTING")
            
            # 1. Macro & Options Intelligence
            logger.info("📊 Processing Global Markets & Options...")
            self.global_engine.run()
            self.options_engine.run()

            # 2. Currency Intelligence
            if self.currency_agent:
                try:
                    logger.info("💱 Running Currency Scan...")
                    # Ensure it has kite one last time before running
                    if hasattr(self.currency_agent, 'kite') and not self.currency_agent.kite:
                        self.currency_agent.kite = self.fetcher.kite
                    
                    if hasattr(self.currency_agent, 'run'): self.currency_agent.run()
                    elif hasattr(self.currency_agent, 'scan'): self.currency_agent.scan()
                except Exception as e:
                    logger.error(f"Currency Agent Run Error: {e}")
            
            # 3. News & Education Intelligence
            if self.news_agent:
                try:
                    logger.info("📰 Running News Intelligence...")
                    if hasattr(self.news_agent, 'run'): self.news_agent.run()
                    elif hasattr(self.news_agent, 'scan'): self.news_agent.scan()
                except Exception as e:
                    logger.error(f"News Agent Run Error: {e}")

            logger.info("✅ ALL INTELLIGENCE SEGMENTS COMPLETE")
            
        except Exception as e:
            logger.error(f"❌ System Controller Critical Run Error: {e}")
            print(traceback.format_exc())
