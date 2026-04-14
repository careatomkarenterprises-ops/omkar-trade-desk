"""
Omkar Trade Services - Currency Agent (CDS)
Logic: Mean Reversion & RBI Intervention Footprints
"""
import json
import pandas as pd
from datetime import datetime, timedelta
from src.telegram.poster import send_to_telegram

# Note: You will need a way to initialize Kite here if running as __main__
# For now, this is designed to be called by your main scanner logic

class CurrencyAgent:
    def __init__(self, kite):
        self.kite = kite
        try:
            with open('data/instrument_tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except FileNotFoundError:
            self.tokens = {}

    def scan_currency(self):
        # Focus on the most liquid USDINR and EURINR contracts
        targets = ["CDS:USDINR26APRFUT", "CDS:EURINR26APRFUT"]
        
        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token: 
                print(f"⚠️ Token not found for {symbol}")
                continue
            
            # Fetch Hourly candles to identify the 'Big Picture'
            to_date = datetime.now()
            from_date = to_date - timedelta(days=5)
            
            try:
                candles = self.kite.historical_data(token, from_date, to_date, "60minute")
                df = pd.DataFrame(candles)
                
                if df.empty:
                    print(f"⚠️ No data found for {symbol}")
                    continue

                # --- TEST MODE START ---
                # We are forcing this to True to test the Telegram connection
                if True: 
                    self.alert_currency_setup(symbol, "MANUAL TEST: No Supply Test")
                # --- TEST MODE END ---
                
            except Exception as e:
                print(f"❌ Error scanning {symbol}: {e}")

    def alert_currency_setup(self, symbol, pattern):
        msg = (
            f"💱 **OMKAR ELITE CURRENCY ALERT**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**VSA Pattern:** {pattern}\n"
            f"**Insight:** Market is testing lows with zero selling pressure. High probability of Mean Reversion.\n"
            f"📈 **Target:** Daily VWAP / Pivot Point"
        )
        # Using lowercase 'currency' to match your poster.py mapping
        send_to_telegram("currency", msg)

if __name__ == "__main__":
    # This part is used if you run the script directly for a test
    # Ensure your Kite authentication logic is available here if needed
    pass
