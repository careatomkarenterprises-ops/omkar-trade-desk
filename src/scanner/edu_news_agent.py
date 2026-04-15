import os
import random
from src.telegram.poster import send_to_telegram

class EduNewsAgent:
    def __init__(self):
        self.concepts = [
            {"title": "Stopping Volume", "desc": "When a high volume bar appears on a down-move but the price closes off the low, it indicates institutional absorption (the 'brake')."},
            {"title": "No Supply Test", "desc": "A narrow spread candle on low volume after a decline suggests sellers are exhausted. Prepare for a reversal."},
            {"title": "The Shakeout", "desc": "A rapid price drop designed to trigger retail stop-losses before the big move up begins."}
        ]

    def post_daily_concept(self):
        concept = random.choice(self.concepts)
        msg = (
            f"🎓 **OMKAR ELITE EDUCATION**\n\n"
            f"**Concept:** {concept['title']}\n"
            f"**Logic:** {concept['desc']}\n\n"
            f"🔍 *Master the Volume, Master the Market.*"
        )
        send_to_telegram("education", msg)

    def scan_global_news(self):
        # Placeholder for News API Integration
        msg = (
            f"🌍 **GLOBAL MARKET UPDATE**\n\n"
            f"**Focus:** RBI Policy Outlook & USDINR Stability.\n"
            f"**Sentiment:** Institutional accumulation observed in Nifty Heavyweights.\n"
            f"⚠️ *Monitor Volume Multipliers at 10:30 AM IST.*"
        )
        send_to_telegram("education", msg)

if __name__ == "__main__":
    agent = EduNewsAgent()
    # Post one educational insight per run
    agent.post_daily_concept()
