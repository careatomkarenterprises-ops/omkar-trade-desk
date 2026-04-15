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
        except:
            self.tokens = {}

    def scan_currency(self):
        targets = ["CDS:USDINR26APRFUT", "CDS:EURINR26APRFUT"]
        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token: continue

            try:
                # VSA Analysis logic
                candles = self.kite.historical_data(token, datetime.now()-timedelta(days=5), datetime.now(), "60minute")
                df = pd.DataFrame(candles)
                if df.empty: continue

                # Logic: Low Volume Test at Support
                last_vol = df['volume'].iloc[-1]
                avg_vol = df['volume'].tail(20).mean()
                
                if last_vol < (avg_vol * 0.8):
                    self.alert_currency_setup(symbol, "Institutional No-Supply Test")
            except:
                print(f"🟡 Skipping {symbol} (Market might be closed)")

    def alert_currency_setup(self, symbol, pattern):
        msg = (
            f"💱 **OMKAR ELITE CURRENCY ALERT**\n\n"
            f"**Symbol:** {symbol}\n"
            f"**VSA Pattern:** {pattern}\n"
            f"**Insight:** Smart Money is testing supply. Reversal expected.\n"
            f"⚠️ *Educational purposes only.*"
        )
        send_to_telegram("currency", msg)

if __name__ == "__main__":
    from src.scanner.morning_setup import get_kite_instance
    try:
        kite = get_kite_instance()
        if kite:
            agent = CurrencyAgent(kite)
            agent.scan_currency()
    except:
        print("🚫 System offline: Market is closed.")
