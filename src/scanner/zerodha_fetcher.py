import logging
import os
# Match your actual class name
from src.scanner.zerodha_fetcher import ZerodhaFetcher as DataFetcher
from src.scanner.patterns import PatternDetector
from src.scanner.premarket_engine import PreMarketPredictionEngine
from src.scanner.global_market_engine import GlobalMarketEngine
from src.scanner.options_intelligence_engine import OptionsIntelligenceEngine
from src.telegram.poster import TelegramPoster
from src.agents.currency_agent import CurrencyAgent 
from src.agents.commodity_agent import CommodityAgent

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        try:
            # Initialize core components
            self.fetcher = DataFetcher()
            self.detector = PatternDetector()
            self.premarket = PreMarketPredictionEngine(self.fetcher, self.detector)
            self.global_engine = GlobalMarketEngine()
            self.options_engine = OptionsIntelligenceEngine()
            self.telegram = TelegramPoster()
        except Exception as e:
            logger.error(f"⚠️ Controller Init Warning: {e}")

    def run_premarket(self):
        """Phase 1: Analysis before market opens"""
        try:
            logger.info("🎬 Starting Premarket Routine...")
            global_data = self.global_engine.run()
            
            # Run premarket scan
            results = self.premarket.run(global_data=global_data)
            
            # Send results to Telegram only if they exist
            if results:
                self.telegram.send_message(f"🚀 TOP PREMARKET SETUPS FOUND: {len(results)}")
            else:
                self.telegram.send_message("🔍 Premarket: No specific volume shocks detected.")
                
        except Exception as e:
            logger.error(f"❌ Premarket routine failed: {e}")

    def run_live_session(self):
        """Phase 2: Continuous monitoring during market hours"""
        try:
            # 1. Update Macro Bias
            global_data = self.global_engine.run()
            
            # 2. Update Options (FII/DII logic)
            self.options_engine.run()

            # 3. Currency & Commodity (Fixed Agent calls)
            try:
                CurrencyAgent().scan() 
                CommodityAgent().scan()
            except Exception as e:
                logger.warning(f"Non-critical agent failure: {e}")

            logger.info("✅ Live Cycle Completed Successfully")
            
        except Exception as e:
            logger.error(f"❌ Live session cycle error: {e}")
