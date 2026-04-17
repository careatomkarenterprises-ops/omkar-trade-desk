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
                
                if cls:
                    try:
                        # Attempt 1: Standard init
                        self.agents[file_name] = cls(kite=kite)
                    except TypeError:
                        # Attempt 2: If agent doesn't take 'kite' in __init__
                        self.agents[file_name] = cls()
                        if hasattr(self.agents[file_name], 'kite'):
                            self.agents[file_name].kite = kite
                    
                    logger.info(f"✅ Loaded {class_name}")
            except Exception as e:
                logger.warning(f"⏩ Skipping {file_name}: {e}")

    def run_agent_safely(self, name, agent):
        try:
            logger.info(f"📡 Running {name.upper()}...")
            # Try all common execution method names
            methods = ['run', 'scan', 'execute', 'analyze_news', 'start', 'post_updates']
            executed = False
            for m in methods:
                method = getattr(agent, m, None)
                if callable(method):
                    method()
                    executed = True
                    break
            
            if not executed:
                logger.warning(f"❓ {name} has no recognized run method.")
        except Exception as e:
            logger.error(f"❌ {name} execution error: {e}")

    def run(self):
        try:
            logger.info("🚀 OMKAR INTELLIGENCE CYCLE STARTING")
            
            # 1. Global Context
            self.global_engine.run()
            self.options_engine.run()

            # 2. Sequential Agent Execution
            for name, agent in self.agents.items():
                self.run_agent_safely(name, agent)

            logger.info("✅ ALL SYSTEMS OPERATIONAL - SCAN COMPLETE")
            
        except Exception as e:
            logger.error(f"❌ Critical Controller Failure: {e}")
            print(traceback.format_exc())

    def run_live_session(self): self.run()
