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
            from src.scanner.patterns import PatternDetector
            from src.scanner.global_market_engine import GlobalMarketEngine
            from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
            from src.telegram.poster import TelegramPoster
            
            self.fetcher = ZerodhaFetcher()
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
            # Added 'scan_fno' to priority to fix your F&O agent issue
            priority_methods = ['run', 'scan', 'scan_fno', 'analyze_news', 'execute']
            method = None
            for m in priority_methods:
                if hasattr(agent, m):
                    method = getattr(agent, m)
                    break
            
            if method:
                report = method()
                if report:
                    self.route_report(name, report)
            else:
                logger.warning(f"❓ {name} has no recognized execution method")
        except Exception as e:
            logger.error(f"❌ {name} execution failed: {e}")

    def route_report(self, agent_name, report):
        if not report: return
        # Routing Logic for your 3 consolidated channels
        if agent_name in ['fno_agent', 'commodity_agent', 'currency_agent']:
            self.telegram.send_message('premium', report)
        elif agent_name in ['edu_news_agent']:
            self.telegram.send_message('education', report)
        else:
            self.telegram.send_message('free', report)

    def run_market_intelligence(self):
        now = datetime.now()
        current_time = now.hour * 100 + now.minute
        
        # 1. Run Global Engine first to get data for EOD
        global_data = self.global_engine.run() 

        # 2. Live Market Agents
        for name, agent in self.agents.items():
            self.run_agent_safely(name, agent)

        # 3. FIX: EOD Review (Passing the required global_data)
        if current_time >= 1535:
            logger.info("🌙 Phase: EOD REVIEW")
            from src.scanner.eod_engine import EODEngine
            eod = EODEngine()
            # Pass global_data to fix the crash
            summary = eod.run(global_data=global_data) 
            self.telegram.send_message('free', summary)

    def run(self):
        self.run_market_intelligence()

if __name__ == "__main__":
    controller = SystemController()
    controller.run()
