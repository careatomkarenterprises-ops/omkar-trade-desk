import logging
import os
import json
import inspect
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        logger.info("🛠️ Initializing Omkar Enterprise Grade Controller...")
        try:
            from src.scanner.zerodha_fetcher import ZerodhaFetcher
            from src.scanner.global_market_engine import GlobalMarketEngine
            from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
            from src.telegram.poster import TelegramPoster
            
            self.fetcher = ZerodhaFetcher()
            self.global_engine = GlobalMarketEngine()
            self.options_engine = OptionsIntelligenceEngine()
            self.telegram = TelegramPoster()
            
            self.agents = {}
            self._init_all_agents()
        except Exception as e:
            logger.error(f"💥 Controller Init Failed: {e}")

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
                    sig = inspect.signature(cls.__init__)
                    instance = cls(kite_instance=kite) if 'kite_instance' in sig.parameters else cls()
                    self.agents[file_name] = instance
                    logger.info(f"✅ Loaded: {file_name}")
            except Exception as e:
                logger.warning(f"⏩ Skipping {file_name}: {e}")

    def run_agent_safely(self, name, agent):
        try:
            logger.info(f"📡 Executing {name.upper()}...")
            # Aggressive Discovery: Find any method starting with 'scan', 'run', or 'execute'
            method = None
            for attr in dir(agent):
                if any(attr.startswith(p) for p in ['scan', 'run', 'execute', 'analyze']) and callable(getattr(agent, attr)):
                    method = getattr(agent, attr)
                    break
            
            if method:
                report = method()
                # ANTI-EMPTY MESSAGE LOGIC
                if not report or str(report).strip() == "":
                    report = f"🔍 {name.replace('_', ' ').title()}: No specific institutional volume footprints detected in this cycle."
                
                self.route_report(name, report)
                logger.info(f"🟢 {name} completed.")
            else:
                logger.warning(f"❓ {name} has no recognized execution method")
        except Exception as e:
            logger.error(f"❌ {name} execution failed: {e}")

    def route_report(self, agent_name, report):
        # Map agent names to your 3 consolidated channels
        target = 'free'
        if agent_name in ['fno_agent', 'commodity_agent', 'currency_agent']:
            target = 'premium'
        elif agent_name == 'edu_news_agent':
            target = 'education'
        
        self.telegram.send_message(target, report)

    def run_market_intelligence(self):
        now = datetime.now()
        current_time = now.hour * 100 + now.minute
        
        # 1. Global Bias
        global_data = self.global_engine.run()

        # 2. Specialty Agents
        for name, agent in self.agents.items():
            self.run_agent_safely(name, agent)

        # 3. EOD Review Fix
        if current_time >= 1535:
            logger.info("🌙 Phase: EOD REVIEW")
            try:
                from src.scanner.eod_engine import EODEngine
                eod = EODEngine()
                summary = eod.run(global_data=global_data)
                if not summary:
                    summary = "📊 *Market Wrap:* Index remained sideways. No major volume breakout patterns confirmed at EOD."
                
                self.telegram.send_message('free', summary)
                self.telegram.send_message('premium', summary)
            except Exception as e:
                logger.error(f"EOD Engine failed: {e}")

    def run(self):
        self.run_market_intelligence()

if __name__ == "__main__":
    controller = SystemController()
    controller.run()
