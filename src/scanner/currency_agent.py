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

    def analyze_vsa_and_box(self, df):
        """Omkar Core Logic: Box Breakout + Volume Spike + V-Pattern"""
        if len(df) < 30: return None
        
        # 1. Box/Range Logic
        recent_high = df['high'].iloc[-20:-1].max()
        recent_low = df['low'].iloc[-20:-1].min()
        current_close = df['close'].iloc[-1]
        current_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].iloc[-20:].mean()

        # Logic: Box Breakout with Volume Confirmation
        if current_close > recent_high and current_vol > (avg_vol * 1.5):
            return f"📦 BOX BREAKOUT (Resistance Broken at {recent_high})"
        
        if current_close < recent_low and current_vol > (avg_vol * 1.5):
            return f"⚠️ BOX BREAKDOWN (Support Broken at {recent_low})"

        # 2. Volume Spike Logic (Institutional Footprint)
        if current_vol > (avg_vol * 2.5):
            return f"🚀 GHOST PUMP / VOLUME SPIKE ({round(current_vol/avg_vol, 1)}x Average)"

        # 3. V-Shape Recovery Logic
        volumes = df['volume'].values[-10:]
        valley_idx = np.argmin(volumes[-5:])
        if valley_idx < 3:
            if df['close'].iloc[-1] > df['close'].iloc[-5 + valley_idx] * 1.005:
                return "📈 V-SHAPE VOLUME RECOVERY"

        return None

    def scan(self):
        # List of symbols to monitor
        targets = ["CDS:USDINR26APRFUT", "CDS:EURINR26APRFUT", "CDS:GBPINR26APRFUT"]
        
        # Status Heartbeat
        send_to_telegram("currency", "🔍 **Omkar Core Engine:** Scanning 30-min Box & Volume Patterns...")
        
        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token: continue
            try:
                # IMPORTANT: Fetching 30-minute intervals as requested
                data = self.kite.historical_data(token, datetime.now()-timedelta(days=7), datetime.now(), "30minute")
                df = pd.DataFrame(data)
                
                pattern = self.analyze_vsa_and_box(df)
                if pattern:
                    self.post_alert(symbol, pattern, df['close'].iloc[-1])
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")

    def post_alert(self, symbol, pattern, price):
        msg = (
            f"🎯 **OMKAR CORE SIGNAL**\n\n"
            f"**Symbol:** {symbol.split(':')[-1]}\n"
            f"**Price:** {price}\n"
            f"**Signal:** {pattern}\n"
            f"**TF:** 30-Minute Chart\n\n"
            f"⚡ *Institutional activity detected. Watch for the big move.*"
        )
        send_to_telegram("currency", msg)

if __name__ == "__main__":
    kite = get_kite_instance()
    if kite:
        agent = CurrencyAgent(kite)
        agent.scan()
