import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from src.telegram.poster import TelegramPoster
from src.scanner.morning_setup import get_kite_instance

logger = logging.getLogger(__name__)


class CurrencyAgent:

    def __init__(self):
        self.kite = get_kite_instance()
        self.telegram = TelegramPoster()

        try:
            with open('data/instrument_tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except:
            self.tokens = {}

    def analyze_vsa_and_box(self, df):
        if len(df) < 30:
            return None

        recent_high = df['high'].iloc[-20:-1].max()
        recent_low = df['low'].iloc[-20:-1].min()
        current_close = df['close'].iloc[-1]
        current_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].iloc[-20:].mean()

        if current_close > recent_high and current_vol > (avg_vol * 1.5):
            return f"📦 BOX BREAKOUT above {recent_high}"

        if current_close < recent_low and current_vol > (avg_vol * 1.5):
            return f"⚠️ BOX BREAKDOWN below {recent_low}"

        if current_vol > (avg_vol * 2.5):
            return f"🚀 VOLUME SPIKE ({round(current_vol/avg_vol, 1)}x)"

        return None

    def run(self):

        if not self.kite:
            logger.error("❌ Kite not available")
            return

        self.telegram.send_message("free", "💱 Currency Scan Started")

        targets = [
            "CDS:USDINR26APRFUT",
            "CDS:EURINR26APRFUT",
            "CDS:GBPINR26APRFUT"
        ]

        for symbol in targets:

            token = self.tokens.get(symbol)
            if not token:
                continue

            try:
                data = self.kite.historical_data(
                    token,
                    datetime.now() - timedelta(days=7),
                    datetime.now(),
                    "30minute"
                )

                df = pd.DataFrame(data)
                pattern = self.analyze_vsa_and_box(df)

                if pattern:
                    msg = f"💱 {symbol} | {pattern}"
                    self.telegram.send_message("free", msg)

            except Exception as e:
                logger.error(f"{symbol} error: {e}")
