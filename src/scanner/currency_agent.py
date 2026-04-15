import os
import json
import pandas as pd
import numpy as np
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

    def detect_v_pattern(self, data):
        """Your v2.0 Logic: V-Shape Volume Recovery"""
        if len(data) < 10: return None
        volumes = data['volume'].values[-10:]
        closes = data['close'].values[-10:]
        recent_volumes = volumes[-5:]
        valley_idx = np.argmin(recent_volumes)
        
        if valley_idx < 3:
            after_valley = recent_volumes[valley_idx+1:]
            if len(after_valley) >= 2:
                if all(after_valley[i] > after_valley[i-1] for i in range(1, len(after_valley))):
                    valley_price = closes[-5 + valley_idx]
                    if closes[-1] > valley_price * 1.005:
                        return "V-Shape Volume Recovery"
        return None

    def detect_volume_spike(self, data, threshold=1.8):
        """Your v2.0 Logic: Volume Spike"""
        if len(data) < 20: return None
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].iloc[-20:].mean()
        ratio = current_volume / avg_volume if avg_volume > 0 else 0
        if ratio > threshold:
            return f"Institutional Volume Spike ({round(ratio, 1)}x)"
        return None

    def scan(self):
        targets = ["CDS:USDINR26APRFUT", "CDS:EURINR26APRFUT"]
        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token: continue
            try:
                # 60-min timeframe for high-conviction institutional footprints
                data = self.kite.historical_data(token, datetime.now()-timedelta(days=5), datetime.now(), "60minute")
                df = pd.DataFrame(data)
                
                pattern = self.detect_v_pattern(df) or self.detect_volume_spike(df)
                if pattern:
                    self.post_alert(symbol, pattern, df['close'].iloc[-1])
            except Exception as e:
                print(f"Skipping {symbol}: {e}")

    def post_alert(self, symbol, pattern, price):
        msg = (
            f"💱 **OMKAR ELITE CURRENCY ALERT**\n\n"
            f"**Symbol:** {symbol.split(':')[-1]}\n"
            f"**Price:** {price}\n"
            f"**Pattern:** {pattern}\n"
            f"**Strategy:** Omkar V-Logic v2.0\n\n"
            f"🔍 *Watch for follow-through volume. Educational only.*"
        )
        send_to_telegram("currency", msg)

if __name__ == "__main__":
    kite = get_kite_instance()
    if kite:
        agent = CurrencyAgent(kite)
        agent.scan()
