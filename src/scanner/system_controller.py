import logging
import os
import json
import traceback
import inspect

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        logger.info("🛠️ Initializing Omkar Enterprise Grade Controller...")
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
            
            self._ensure_data_integrity()
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
        kite = self.fetcher.kite
        # Mapping files to their primary class names
        agent_configs = {
            'currency_agent': 'CurrencyAgent',
            'fno_agent': 'FnOAgent',
            'swing_agent': 'SwingAgent',
            'commodity_agent': 'CommodityAgent',
            'edu_news_agent': 'EduNewsAgent'
        }

        for file_name, class_name in agent_configs.items():
            try:
                module = __import__(f"src.scanner.{file_name}", fromlist=[class_name])
                cls = getattr(module, class_name, None)
                
                # If specific class name fails, look for any class containing 'Agent'
                if not cls:
                    for attr in dir(module):
                        if 'Agent' in attr: cls = getattr(module, attr)

                if cls:
                    # Dynamically check for 'kite' vs 'kite_instance' to avoid init errors
                    sig = inspect.signature(cls.__init__)
                    if 'kite_instance' in sig.parameters:
                        self.agents[file_name] = cls(kite_instance=kite)
                    elif 'kite' in sig.parameters:
                        self.agents[file_name] = cls(kite=kite)
                    else:
                        self.agents[file_name] = cls()
                    
                    logger.info(f"✅ Successfully Loaded: {file_name}")
            except Exception as e:
                logger.warning(f"⏩ Skipping {file_name}: {e}")

    def run_agent_safely(self, name, agent):
        try:
            logger.info(f"📡 Executing {name.upper()}...")
            # Try all known execution method names used across your files
            methods = ['run', 'scan', 'post_education', 'analyze_news', 'execute']
            for m in methods:
                method = getattr(agent, m, None)
                if callable(method):
                    method()
                    logger.info(f"🟢 {name} completed via {m}()")
                    return
            logger.warning(f"❓ {name} has no recognized execution method")
        except Exception as e:
            logger.error(f"❌ {name} execution failed: {e}")

    def run(self):
        try:
            logger.info("🚀 OMKAR INTELLIGENCE CYCLE STARTING")
            
            # 1. Run Core Engines (Market context & Options)
            self.global_engine.run()
            self.options_engine.run()

            # 2. Run Individual Specialized Agents
            for name, agent in self.agents.items():
                self.run_agent_safely(name, agent)

            logger.info("✅ ALL SYSTEMS OPERATIONAL - SCAN COMPLETE")
        except Exception as e:
            logger.error(f"❌ Critical System Failure: {e}")
            print(traceback.format_exc())

    def run_live_session(self): 
        self.run()
