import os
import json
import pandas as pd
from datetime import datetime, timedelta
from src.telegram.poster import send_to_telegram
from src.scanner.morning_setup import get_kite_instance

class CurrencyAgent:
    def __init__(self, kite):
        self.kite = kite
        try:
            with open('data/instrument_tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except:
            self.tokens = {}

    def analyze_vsa(self, df):
        """Core Omkar Logic: Institutional Footprint Detection"""
        if len(df) < 20: return None
        
        last_bar = df.iloc[-1]
        avg_vol = df['volume'].tail(20).mean()
        
        # Logic 1: No Supply Test (Low volume, narrow spread)
        if last_bar['volume'] < (avg_vol * 0.7):
            return "Institutional No-Supply Test (Potential Reversal)"
        
        # Logic 2: Volume Multiplier (Ghost Pump)
        if last_bar['volume'] > (avg_vol * 2.5):
            return "Volume Multiplier Detected (Institutional Entry)"
            
        return None

    def scan(self):
        # Targets for Currency Segment
        targets = ["CDS:USDINR26APRFUT", "CDS:EURINR26APRFUT"]
        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token: continue

            try:
                # Get 60-min candles for clear trend analysis
                data = self.kite.historical_data(token, datetime.now()-timedelta(days=5), datetime.now(), "60minute")
                df = pd.DataFrame(data)
                
                pattern = self.analyze_vsa(df)
                if pattern:
                    self.post_alert(symbol, pattern, df['close'].iloc[-1])
            except Exception as e:
                print(f"⚠️ Market closed or error for {symbol}: {e}")

    def post_alert(self, symbol, pattern, price):
        msg = (
            f"💱 **OMKAR ELITE CURRENCY ALERT**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**Price:** {price}\n"
            f"**Pattern:** {pattern}\n"
            f"**Insight:** Professional money footprint detected. Watch for volume confirmation.\n\n"
            f"⚠️ *Educational purposes only.*"
        )
        send_to_telegram("currency", msg)

if __name__ == "__main__":
    kite = get_kite_instance()
    if kite:
        agent = CurrencyAgent(kite)
        agent.scan()
