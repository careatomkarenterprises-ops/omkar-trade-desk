import os
import random
import logging
from src.telegram.poster import TelegramPoster

# Using a safer import for kite instance
try:
    from src.scanner.morning_setup import get_kite_instance
except ImportError:
    get_kite_instance = lambda: None

logger = logging.getLogger(__name__)

class EduNewsAgent:
    def __init__(self, kite=None):
        self.kite = kite or get_kite_instance()
        self.telegram = TelegramPoster()

    def run(self):
        """Standardized entry point for the System Controller"""
        logger.info("📡 EduNewsAgent: Starting Education Cycle...")
        self.post_education()

    def post_education(self):
        concepts = [
            {"title": "The Shakeout", "desc": "A rapid price drop designed to trigger retail stop-losses before a rally."},
            {"title": "Stopping Volume", "desc": "High volume on a down-move where price refuses to fall further. Professional buying detected."},
            {"title": "No Supply Test", "desc": "Low volume on a narrow spread candle, indicating the sellers are exhausted and a rally is likely."},
            {"title": "VCP (Volatility Contraction)", "desc": "Price moving in tighter ranges on lower volume, preparing for a massive institutional breakout."}
        ]
        concept = random.choice(concepts)
        
        real_price = "Check Terminal"
        try:
            if self.kite:
                # Fetching REAL LIVE Price from NSE
                rel_data = self.kite.quote("NSE:RELIANCE")
                if rel_data and "NSE:RELIANCE" in rel_data:
                    real_price = rel_data["NSE:RELIANCE"]["last_price"]
        except Exception as e:
            logger.warning(f"Could not fetch Reliance price: {e}")

        msg = (
            f"🎓 **OMKAR ELITE EDUCATION**\n\n"
            f"**Concept:** {concept['title']}\n"
            f"**Logic:** {concept['desc']}\n\n"
            f"📊 **Real-Time Analysis (RELIANCE):**\n"
            f"Current Price: ₹{real_price}\n"
            f"Status: Analyzing Volume Footprint...\n\n"
            f"🔍 *Master the Volume, Master the Market.*"
        )
        
        try:
            # Check if education secret exists, else force fallback to free
            if not os.getenv("CHANNEL_EDUCATION"):
                logger.error("❌ CHANNEL_EDUCATION not found in env, falling back to FREE")
                self.telegram.send_message("free", msg)
            else:
                self.telegram.send_message("education", msg)
                logger.info("✅ Educational post sent to Education Channel.")
        except Exception as e:
            logger.error(f"Failed to send Edu post: {e}")
            self.telegram.send_message("free", msg)

if __name__ == "__main__":
    agent = EduNewsAgent()
    agent.run()
