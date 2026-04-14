"""
Omkar Trade Services - Currency Agent (CDS)
FORCED TEST VERSION
"""
import os
from src.telegram.poster import send_to_telegram

class CurrencyAgent:
    def __init__(self, kite=None):
        self.kite = kite

    def scan_currency(self):
        # We skip all logic and just trigger the alert
        print("🚀 FORCING TELEGRAM TEST MESSAGE...")
        self.alert_currency_setup("USDINR-TEST", "CONNECTION VERIFIED")

    def alert_currency_setup(self, symbol, pattern):
        msg = (
            f"💱 **OMKAR ELITE SYSTEM TEST**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**Status:** Telegram Connection Active ✅\n"
            f"**Note:** Infrastructure is ready for tomorrow's market open."
        )
        send_to_telegram("currency", msg)

if __name__ == "__main__":
    # This allows the runner to execute this file directly
    agent = CurrencyAgent()
    agent.scan_currency()
