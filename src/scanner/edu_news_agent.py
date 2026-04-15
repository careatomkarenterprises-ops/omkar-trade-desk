import os
import random
from src.telegram.poster import send_to_telegram
from src.scanner.morning_setup import get_kite_instance

class EduNewsAgent:
    def __init__(self, kite):
        self.kite = kite

    def post_education(self):
        # Master VSA Concepts for the Elite Brand
        concepts = [
            {"title": "The Shakeout", "desc": "A rapid price drop designed to trigger retail stop-losses before a rally."},
            {"title": "Stopping Volume", "desc": "High volume on a down-move where price refuses to fall further. Buying detected."},
            {"title": "Effort vs Result", "desc": "High volume but no price movement usually means a trend change is coming."}
        ]
        
        concept = random.choice(concepts)
        
        # Fetch REAL Reliance price to ensure accuracy
        try:
            rel_data = self.kite.quote("NSE:RELIANCE")
            real_price = rel_data["NSE:RELIANCE"]["last_price"]
        except:
            real_price = "Market Closed"

        msg = (
            f"🎓 **OMKAR ELITE EDUCATION**\n\n"
            f"**Concept:** {concept['title']}\n"
            f"**Logic:** {concept['desc']}\n\n"
            f"📊 **Market Insight (RELIANCE):**\n"
            f"Current Live Price: {real_price}\n"
            f"Sentiment: Watch for '{concept['title']}' patterns today.\n\n"
            f"🔍 *Master the Volume, Master the Market.*"
        )
        send_to_telegram("education", msg)

if __name__ == "__main__":
    kite = get_kite_instance()
    if kite:
        agent = EduNewsAgent(kite)
        agent.post_education()
