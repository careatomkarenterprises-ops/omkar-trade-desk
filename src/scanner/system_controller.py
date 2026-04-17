import logging
import os
import inspect
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        logger.info("🛠️ Initializing Omkar Enterprise Grade Controller...")
        try:
            from src.scanner.zerodha_fetcher import ZerodhaFetcher
            from src.scanner.global_market_engine import GlobalMarketEngine
            from src.telegram.poster import TelegramPoster
            
            self.fetcher = ZerodhaFetcher()
            self.global_engine = GlobalMarketEngine()
            self.telegram = TelegramPoster()
            self.agents = {}
            self._init_all_agents()
        except Exception as e:
            logger.error(f"💥 Controller Init Failed: {e}")

    def _init_all_agents(self):
        kite = self.fetcher.kite
        agent_configs = {'fno_agent': 'FnOAgent', 'swing_agent': 'SwingAgent', 
                         'commodity_agent': 'CommodityAgent', 'currency_agent': 'CurrencyAgent',
                         'edu_news_agent': 'EduNewsAgent'}
        for file_name, class_name in agent_configs.items():
            try:
                module = __import__(f"src.scanner.{file_name}", fromlist=[class_name])
                cls = getattr(module, class_name, None)
                if cls:
                    sig = inspect.signature(cls.__init__)
                    self.agents[file_name] = cls(kite_instance=kite) if 'kite_instance' in sig.parameters else cls()
                    logger.info(f"✅ Loaded: {file_name}")
            except Exception as e:
                logger.warning(f"⏩ Skipping {file_name}: {e}")

    def run_agent_safely(self, name, agent):
        try:
            logger.info(f"📡 Executing {name.upper()}...")
            report = None
            
            # ✅ FIX: Specifically target your F&O function name
            if name == 'fno_agent':
                data = agent.scan_institutional_build(symbol="NIFTY")
                if data:
                    report = "🏦 *Institutional F&O Build-up*\n\n"
                    for item in data:
                        report += f"🔹 {item['expiry_type']}: {item['sentiment']} @ {item['price']}\n"
            else:
                # Standard discovery for others
                for m in ['run', 'scan', 'execute', 'analyze_news']:
                    if hasattr(agent, m):
                        report = getattr(agent, m)()
                        break
            
            if report:
                target = 'premium' if name in ['fno_agent', 'commodity_agent', 'currency_agent'] else ('education' if name == 'edu_news_agent' else 'free')
                self.telegram.send_message(target, report)
        except Exception as e:
            logger.error(f"❌ {name} execution failed: {e}")

    def run(self):
        current_time = datetime.now().hour * 100 + datetime.now().minute
        global_data = self.global_engine.run()
        
        for name, agent in self.agents.items():
            self.run_agent_safely(name, agent)

        # ✅ FIX: Trigger EOD and pass the required global_data
        if current_time >= 1535:
            from src.scanner.eod_engine import EODEngine
            summary = EODEngine().run(global_data=global_data)
            self.telegram.send_message('free', summary)

if __name__ == "__main__":
    SystemController().run()
