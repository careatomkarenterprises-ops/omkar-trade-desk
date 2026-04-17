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
        # Mapping file names to class names
        agent_map = {
            'fno_agent': 'FnOAgent', 
            'swing_agent': 'SwingAgent', 
            'commodity_agent': 'CommodityAgent', 
            'currency_agent': 'CurrencyAgent',
            'edu_news_agent': 'EduNewsAgent'
        }
        for file, cls_name in agent_map.items():
            try:
                mod = __import__(f"src.scanner.{file}", fromlist=[cls_name])
                cls = getattr(mod, cls_name)
                sig = inspect.signature(cls.__init__)
                # Inject kite if the agent expects it
                self.agents[file] = cls(kite_instance=kite) if 'kite_instance' in sig.parameters else cls()
                logger.info(f"✅ Loaded: {file}")
            except Exception as e:
                logger.warning(f"⏩ Skipping {file}: {e}")

    def run_agent_safely(self, name, agent):
        try:
            logger.info(f"📡 Executing {name.upper()}...")
            report = None
            
            # 1. Custom handling for your specific FnOAgent function
            if name == 'fno_agent' and hasattr(agent, 'scan_institutional_build'):
                data = agent.scan_institutional_build(symbol="NIFTY")
                if data:
                    report = "🏦 *Institutional F&O Build-up*\n\n"
                    for item in data:
                        report += f"🔹 {item['expiry_type']}: {item['sentiment']} @ {item['price']}\n"
            
            # 2. General handling for other agents
            else:
                for m in ['run', 'scan', 'execute', 'analyze_news']:
                    if hasattr(agent, m):
                        report = getattr(agent, m)()
                        break
            
            if report:
                # Determine target channel
                target = 'premium' if name in ['fno_agent', 'commodity_agent', 'currency_agent'] else ('education' if name == 'edu_news_agent' else 'free')
                
                # Send and check success
                sent = self.telegram.send_message(target, report)
                
                # FALLBACK: If Premium/Edu fails, send to FREE channel
                if not sent and target != 'free':
                    logger.warning(f"⚠️ {target} failed. Redirecting to FREE channel.")
                    self.telegram.send_message('free', f"📢 *[{target.upper()} SIGNAL]*\n{report}")

        except Exception as e:
            logger.error(f"❌ {name} failed: {e}")

    def run(self):
        # 1. Get Global Data
        global_data = self.global_engine.run()
        
        # 2. Run All Agents
        for name, agent in self.agents.items():
            self.run_agent_safely(name, agent)

        # 3. Trigger EOD Summary (After 3:35 PM)
        if datetime.now().hour * 100 + datetime.now().minute >= 1535:
            from src.scanner.eod_engine import EODEngine
            eod_msg = EODEngine().run(global_data=global_data)
            self.telegram.send_message('free', eod_msg)

if __name__ == "__main__":
    SystemController().run()
