"""
Omkar Trade Services - Currency Agent (CDS)
Logic: Mean Reversion & RBI Intervention Footprints
"""
import json
import pandas as pd
from datetime import datetime, timedelta
from src.telegram.poster import send_to_telegram

class CurrencyAgent:
    def __init__(self, kite):
        self.kite = kite
        with open('data/instrument_tokens.json', 'r') as f:
            self.tokens = json.load(f)

    def scan_currency(self):
        # Focus on the most liquid USDINR Current Month Future
        # Note: morning_setup.py maps these to the correct expiry tokens
        targets = ["CDS:USDINR26APRFUT", "CDS:EURINR26APRFUT"]
        
        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token: continue
            
            # Fetch Hourly candles to identify the 'Big Picture'
            to_date = datetime.now()
            from_date = to_date - timedelta(days=5)
            candles = self.kite.historical_data(token, from_date, to_date, "60minute")
            df = pd.DataFrame(candles)
            
            # VSA Logic: No Supply / No Demand
            # Low Volume test of a previous support = Institutional 'No Supply'
            last_candle = df.iloc[-1]
            prev_lows = df['low'].tail(20).min()
            avg_vol = df['volume'].tail(20).mean()

            # Detection: Testing lows on very low volume (Smart money not selling)
            if last_candle['low'] <= (prev_lows * 1.0005) and last_candle['volume'] < (0.7 * avg_vol):
                self.alert_currency_setup(symbol, "No Supply Test (Potential Reversal)")

    def alert_currency_setup(self, symbol, pattern):
        msg = (
            f"💱 **OMKAR ELITE CURRENCY ALERT**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**VSA Pattern:** {pattern}\n"
            f"**Insight:** Market is testing lows with zero selling pressure. High probability of Mean Reversion.\n"
            f"📈 **Target:** Daily VWAP / Pivot Point"
        )
        send_to_telegram("CURRENCY", msg)

if __name__ == "__main__":
    # The main workflow calls this via the .yml file
    pass
