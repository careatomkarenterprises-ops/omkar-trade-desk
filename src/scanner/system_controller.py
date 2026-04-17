import logging
import os
import json
import traceback

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        logger.info("🛠️ Initializing Omkar Full-Stack Controller...")
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
            
            # Step 1: Fix Data/Tokens
            self._ensure_data_integrity()
            
            # Step 2: Initialize All Available Agents
            self.agents = {}
            self._init_all_agents()
            
        except Exception as e:
            logger.error(f"💥 Controller Init Failed: {e}")

    def _ensure_data_integrity(self):
        if not os.path.exists('data'): os.makedirs('data')
        token_path = 'data/instrument_tokens.json'
        if not os.path.exists(token_path):
            try:
                instruments = self.fetcher.kite.instruments()
                tokens = {f"{inst['exchange']}:{inst['tradingsymbol']}": inst['instrument_token'] for inst in instruments}
                with open(token_path, 'w') as f: json.dump(tokens, f)
                logger.info(f"✅ Generated {len(tokens)} tokens.")
            except Exception as e: logger.error(f"Token Gen Failed: {e}")

    def _init_all_agents(self):
        """Loads every agent from your scanner folder"""
        kite = self.fetcher.kite
        
        # Currency Agent
        try:
            from src.scanner.currency_agent import CurrencyAgent
            self.agents['currency'] = CurrencyAgent(kite=kite)
        except: logger.warning("Currency Agent skip")

        # FNO / Options Agent
        try:
            from src.scanner.fno_agent import FNOAgent
            self.agents['fno'] = FNOAgent(kite=kite)
        except: logger.warning("FNO Agent skip")

        # Swing Trading Agent
        try:
            from src.scanner.swing_agent import SwingAgent
            self.agents['swing'] = SwingAgent(kite=kite)
        except: logger.warning("Swing Agent skip")

        # Commodity Agent
        try:
            from src.scanner.commodity_agent import CommodityAgent
            self.agents['commodity'] = CommodityAgent(kite=kite)
        except: logger.warning("Commodity Agent skip")

        # News Agent
        try:
            import src.scanner.edu_news_agent as news_mod
            cls = getattr(news_mod, 'EduNewsAgent', getattr(news_mod, 'NewsAgent', None))
            if cls: self.agents['news'] = cls(kite=kite)
        except: logger.warning("News Agent skip")

    def safe_send(self, channel, message):
        """Prevents crash if a specific telegram channel is not configured"""
        try:
            self.telegram.send_message(channel, message)
        except:
            # Fallback to 'free' channel if specific one fails
            self.telegram.send_message("free", f"[{channel.upper()} ADVISORY]\n{message}")

    def run_agent_safely(self, name, agent):
        """Runs an agent even if its internal method name is different"""
        try:
            logger.info(f"📡 Running {name.upper()} Agent...")
            # Try different common run methods
            for method_name in ['run', 'scan', 'execute', 'start']:
                method = getattr(agent, method_name, None)
                if callable(method):
                    method()
                    return
            logger.warning(f"❓ Agent {name} has no valid run method")
        except Exception as e:
            logger.error(f"❌ {name} Agent Error: {e}")

    def run(self):
        try:
            logger.info("🚀 OMKAR FULL SYSTEM SCAN STARTING")
            
            # 1. Global Market Context
            self.global_engine.run()
            self.options_engine.run()

            # 2. Run All Individual Agents
            for name, agent in self.agents.items():
                self.run_agent_safely(name, agent)

            logger.info("✅ ALL SYSTEMS OPERATIONAL - SCAN COMPLETE")
            
        except Exception as e:
            logger.error(f"❌ Critical Controller Failure: {e}")
            print(traceback.format_exc())

    def run_live_session(self): self.run()
