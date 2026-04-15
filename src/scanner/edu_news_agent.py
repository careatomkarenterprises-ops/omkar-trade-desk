import os
import random
from src.telegram.poster import send_to_telegram
from src.scanner.morning_setup import get_kite_instance

class EduNewsAgent:
    def __init__(self, kite):
        self.kite = kite

    def post_education(self):
        concepts = [
            {"title": "The Shakeout", "desc": "A rapid price drop designed to trigger retail stop-losses before a rally."},
            {"title": "Stopping Volume", "desc": "High volume on a down-move where price refuses to fall further. Buying detected."},
            {"title": "No Supply Test", "desc": "Low volume on a narrow spread candle, indicating the sellers are exhausted."}
        ]
        concept = random.choice(concepts)
        
        try:
            # Fetching REAL LIVE Price from NSE
            rel_data = self.kite.quote("NSE:RELIANCE")
            real_price = rel_data["NSE:RELIANCE"]["last_price"]
        except:
            real_price = "Check Terminal"

        msg = (
            f"🎓 **OMKAR ELITE EDUCATION**\n\n"
            f"**Concept:** {concept['title']}\n"
            f"**Logic:** {concept['desc']}\n\n"
            f"📊 **Real-Time Analysis (RELIANCE):**\n"
            f"Current Price: ₹{real_price}\n"
            f"Status: Analyzing Volume Footprint...\n\n"
            f"🔍 *Master the Volume, Master the Market.*"
        )
        send_to_telegram("education", msg)

if __name__ == "__main__":
    kite = get_kite_instance()
    if kite:
        agent = EduNewsAgent(kite)
        agent.post_education()
