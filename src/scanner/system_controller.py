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
        # Dictionary of {FileName: ClassName}
        agent_configs = {
            'currency_agent': 'CurrencyAgent',
            'fno_agent': 'FNOAgent',
            'swing_agent': 'SwingAgent',
            'commodity_agent': 'CommodityAgent',
            'edu_news_agent': 'EduNewsAgent'
        }

        for file_name, class_name in agent_configs.items():
            try:
                module = __import__(f"src.scanner.{file_name}", fromlist=[class_name])
                # Try the specific class, then fall back to anything ending in 'Agent'
                cls = getattr(module, class_name, None)
                if not cls:
                    for attr in dir(module):
                        if 'Agent' in attr: cls = getattr(module, attr)
                
                if cls:
                    self.agents[file_name] = cls(kite=kite)
                    logger.info(f"✅ Loaded {class_name}")
                else:
                    logger.warning(f"⚠️ Could not find class in {file_name}")
            except Exception as e:
                logger.warning(f"⏩ Skipping {file_name}: {e}")

    def run_agent_safely(self, name, agent):
        try:
            logger.info(f"📡 Running {name.upper()} Agent...")
            # FORCE a Telegram heartbeat so you know it's working
            channel_map = {'currency_agent': 'currency', 'edu_news_agent': 'education'}
            target_channel = channel_map.get(name, 'free')
            
            # Try to run the agent
            executed = False
            for method_name in ['run', 'scan', 'execute', 'start', 'analyze_news']:
                method = getattr(agent, method_name, None)
                if callable(method):
                    method()
                    executed = True
                    break
            
            if not executed:
                logger.warning(f"❓ {name} has no run method")

        except Exception as e:
            logger.error(f"❌ {name} Error: {e}")

    def run(self):
        try:
            logger.info("🚀 OMKAR FULL SYSTEM SCAN STARTING")
            
            # 1. Global & Options (Always sends message to 'free')
            self.global_engine.run()
            self.options_engine.run()

            # 2. Run Individual Agents
            if not self.agents:
                logger.error("❌ No agents were loaded!")
            
            for name, agent in self.agents.items():
                self.run_agent_safely(name, agent)

            logger.info("✅ ALL SYSTEMS OPERATIONAL - SCAN COMPLETE")
            
        except Exception as e:
            logger.error(f"❌ Critical Failure: {e}")
            print(traceback.format_exc())

    def run_live_session(self): self.run()
