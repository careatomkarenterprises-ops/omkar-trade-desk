"""
Omkar Trade Services - Commodity Agent (MCX)
Logic: VSA "Effort vs Result" on Gold, Silver, and Crude Oil
"""
import json
import pandas as pd
from datetime import datetime, timedelta
from src.telegram.poster import send_to_telegram

class CommodityAgent:
    def __init__(self, kite):
        self.kite = kite
        with open('data/instrument_tokens.json', 'r') as f:
            self.tokens = json.load(f)

    def scan_mcx(self):
        # Focus on the most liquid MCX contracts
        targets = ["MCX:GOLD26JUNFUT", "MCX:SILVER26MAYFUT", "MCX:CRUDEOIL26APRFUT"]
        
        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token: continue
            
            # Fetch 15-minute candles for intraday VSA
            to_date = datetime.now()
            from_date = to_date - timedelta(days=2)
            candles = self.kite.historical_data(token, from_date, to_date, "15minute")
            df = pd.DataFrame(candles)
            
            # VSA Logic: Effort vs Result
            # High Volume (Effort) but Small Price Move (No Result) = Institutional Absorption
            last_vol = df.iloc[-1]['volume']
            avg_vol = df['volume'].tail(20).mean()
            price_spread = abs(df.iloc[-1]['high'] - df.iloc[-1]['low'])
            
            if last_vol > (2 * avg_vol) and price_spread < (df['high'] - df['low']).tail(20).mean():
                self.alert_institutional_activity(symbol, "Absorption / Hidden Demand")

    def alert_institutional_activity(self, symbol, pattern):
        msg = (
            f"🪙 **OMKAR ELITE COMMODITY ALERT**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**VSA Signal:** {pattern}\n"
            f"**Observation:** Institutional 'Smart Money' is absorbing supply here.\n"
            f"⚠️ *Decision Support: Watch for breakout above candle high.*"
        )
        send_to_telegram("COMMODITY", msg)

if __name__ == "__main__":
    # Initialization logic here
    pass
