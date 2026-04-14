import json
import pandas as pd
from datetime import datetime, timedelta
from src.telegram.poster import send_to_telegram

class CurrencyAgent:
    def __init__(self, kite):
        self.kite = kite
        try:
            with open('data/instrument_tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except FileNotFoundError:
            self.tokens = {}

    def scan_currency(self):
        targets = ["CDS:USDINR26APRFUT", "CDS:EURINR26APRFUT"]
        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token: 
                continue

            try:
                # Fetch 60min candles for VSA analysis
                candles = self.kite.historical_data(token, datetime.now()-timedelta(days=5), datetime.now(), "60minute")
                df = pd.DataFrame(candles)
                if df.empty: continue

                # VSA LOGIC: No Supply / Low Volume Test
                last_vol = df['volume'].iloc[-1]
                avg_vol = df['volume'].tail(20).mean()
                
                if last_vol < (avg_vol * 0.7):
                    self.alert_currency_setup(symbol, "No Supply Test (Low Volume)")
                
            except Exception as e:
                print(f"❌ Error scanning {symbol}: {e}")

    def alert_currency_setup(self, symbol, pattern):
        msg = (
            f"💱 **OMKAR ELITE CURRENCY ALERT**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**VSA Pattern:** {pattern}\n"
            f"**Insight:** Price testing levels with minimal selling pressure. Potential reversal zone."
        )
        send_to_telegram("currency", msg)

if __name__ == "__main__":
    # This block is used by the .yml engine
    from src.scanner.morning_setup import get_kite_instance
    kite = get_kite_instance()
    if kite:
        agent = CurrencyAgent(kite)
        agent.scan_currency()
