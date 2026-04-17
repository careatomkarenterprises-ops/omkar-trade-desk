import logging
import os
import json
import inspect
from datetime import datetime

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        logger.info("🛠️ Initializing Omkar Enterprise Grade Controller...")
        try:
            # Import core components
            from src.scanner.zerodha_fetcher import ZerodhaFetcher
            from src.scanner.patterns import PatternDetector
            from src.scanner.global_market_engine import GlobalMarketEngine
            from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
            from src.telegram.poster import TelegramPoster
            
            # Initialize core services
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
        """Ensures the data folder and tokens exist for scanning."""
        if not os.path.exists('data'): os.makedirs('data')
        token_path = 'data/instrument_tokens.json'
        if not os.path.exists(token_path) and self.fetcher.kite:
            try:
                instruments = self.fetcher.kite.instruments()
                tokens = {f"{inst['exchange']}:{inst['tradingsymbol']}": inst['instrument_token'] for inst in instruments}
                with open(token_path, 'w') as f: json.dump(tokens, f)
                logger.info(f"✅ Generated {len(tokens)} tokens.")
            except Exception as e: 
                logger.error(f"Token Gen Failed: {e}")

    def _init_all_agents(self):
        """Dynamically loads all agents and prepares them for the 3-channel setup."""
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
                
                if not cls:
                    for attr in dir(module):
                        if 'Agent' in attr: cls = getattr(module, attr)

                if cls:
                    sig = inspect.signature(cls.__init__)
                    # Create the agent instance
                    if 'kite_instance' in sig.parameters:
                        instance = cls(kite_instance=kite)
                    elif 'kite' in sig.parameters:
                        instance = cls(kite=kite)
                    else:
                        instance = cls()
                    
                    self.agents[file_name] = instance
                    logger.info(f"✅ Successfully Loaded: {file_name}")
            except Exception as e:
                logger.warning(f"⏩ Skipping {file_name}: {e}")

    def run_agent_safely(self, name, agent):
        """Executes agent and ensures output is routed to the correct channel."""
        try:
            logger.info(f"📡 Executing {name.upper()}...")
            
            # Step 1: Detect method
            priority_methods = ['run', 'scan', 'analyze_news', 'execute']
            method = None
            for m in priority_methods:
                if hasattr(agent, m) and callable(getattr(agent, m)):
                    method = getattr(agent, m)
                    break
            
            if method:
                report = method()
                # Step 2: Route output based on Agent Type to your 3 main channels
                if report:
                    self.route_report(name, report)
                logger.info(f"🟢 {name} completed successfully.")
            else:
                logger.warning(f"❓ {name} has no recognized execution method")
        except Exception as e:
            logger.error(f"❌ {name} execution failed: {e}")

    def route_report(self, agent_name, report):
        """Routes reports to the 3 Consolidated Channels: Free, Premium, Education"""
        if not report: return

        # Routing Logic
        if agent_name in ['fno_agent', 'commodity_agent', 'currency_agent']:
            # High-value signals go to PREMIUM
            self.telegram.send_message('premium', report)
        elif agent_name in ['edu_news_agent']:
            # Educational/News context goes to EDUCATION
            self.telegram.send_message('education', report)
        elif agent_name in ['swing_agent']:
            # Pre-market or general lists go to FREE to attract users
            self.telegram.send_message('free', report)

    def run_market_intelligence(self):
        """The Main Engine: Runs different logic based on the time of day."""
        now = datetime.now()
        current_time = now.hour * 100 + now.minute
        
        logger.info(f"🚀 OMKAR INTELLIGENCE STARTING (Time: {current_time})")

        # 1. Pre-Market Phase (9:00 AM - 9:15 AM)
        if 900 <= current_time <= 915:
            logger.info("🌅 Phase: PRE-OPEN REVIEW")
            from src.scanner.premarket_engine import PreMarketEngine
            pm = PreMarketEngine()
            top_bottom = pm.run()
            self.telegram.send_message('free', top_bottom)

        # 2. Live Market Phase
        self.global_engine.run()
        self.options_engine.run()
        
        for name, agent in self.agents.items():
            self.run_agent_safely(name, agent)

        # 3. EOD Phase (After 3:35 PM)
        if current_time >= 1535:
            logger.info("🌙 Phase: EOD REVIEW")
            from src.scanner.eod_engine import EODEngine
            eod = EODEngine()
            summary = eod.run()
            self.telegram.send_message('free', "📊 *Daily Market Review Complete.*\nFull details in Premium.")
            self.telegram.send_message('premium', summary)

    def run(self):
        self.run_market_intelligence()

if __name__ == "__main__":
    controller = SystemController()
    controller.run()
