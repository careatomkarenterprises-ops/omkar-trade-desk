import logging
import os
import json
import traceback

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        logger.info("🛠️ Initializing Omkar System Controller...")
        try:
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
            
            # ✅ STEP 1: Fix the missing tokens issue immediately
            self._ensure_data_integrity()
            
            self.currency_agent = None
            self.news_agent = None
            self._load_agents_with_context()
            
        except Exception as e:
            logger.error(f"💥 Controller Init Failed: {e}")

    def _ensure_data_integrity(self):
        """Creates data folder and forces token generation if missing"""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        token_path = 'data/instrument_tokens.json'
        if not os.path.exists(token_path):
            logger.info("🔄 Missing tokens! Fetching from Zerodha...")
            try:
                # Get all tradable instruments
                instruments = self.fetcher.kite.instruments()
                tokens = {f"{inst['exchange']}:{inst['tradingsymbol']}": inst['instrument_token'] for inst in instruments}
                with open(token_path, 'w') as f:
                    json.dump(tokens, f)
                logger.info(f"✅ Generated {len(tokens)} tokens.")
            except Exception as e:
                logger.error(f"Failed to generate tokens: {e}")

    def _load_agents_with_context(self):
        try:
            from src.scanner.currency_agent import CurrencyAgent
            self.currency_agent = CurrencyAgent(kite=self.fetcher.kite)
            logger.info("✅ Currency Agent Loaded")
        except: logger.warning("⚠️ CurrencyAgent failed load")

        try:
            import src.scanner.edu_news_agent as news_mod
            agent_class = getattr(news_mod, 'EduNewsAgent', getattr(news_mod, 'NewsAgent', None))
            if agent_class:
                self.news_agent = agent_class(kite=self.fetcher.kite)
                logger.info("✅ News Agent Loaded")
        except: logger.warning("⚠️ NewsAgent failed load")

    def run(self):
        try:
            logger.info("🚀 OMKAR INTELLIGENCE CYCLE STARTING")
            
            # 1. Global & Options (Free Channel)
            self.global_engine.run()
            self.options_engine.run()

            # 2. Currency (Currency Channel)
            if self.currency_agent:
                # FORCE HEARTBEAT so you see it's working
                self.telegram.send_message("currency", "🔄 Currency Intelligence: Active & Scanning...")
                self.currency_agent.run()
            
            # 3. News & Education (Education Channel)
            if self.news_agent:
                # FORCE HEARTBEAT
                self.telegram.send_message("education", "📚 Education/News Engine: Active & Monitoring...")
                self.news_agent.run()

            logger.info("✅ ALL INTELLIGENCE SEGMENTS COMPLETE")
            
        except Exception as e:
            logger.error(f"❌ Run Error: {e}")
            print(traceback.format_exc())

    def run_live_session(self):
        self.run()
