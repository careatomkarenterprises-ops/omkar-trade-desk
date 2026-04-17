import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from src.telegram.poster import TelegramPoster
# Added fallback import
try:
    from src.scanner.morning_setup import get_kite_instance
except ImportError:
    get_kite_instance = lambda: None

logger = logging.getLogger(__name__)

class CurrencyAgent:
    def __init__(self, kite=None):
        """
        Modified to accept an existing kite instance.
        This prevents 'Kite not available' errors during live runs.
        """
        self.kite = kite or get_kite_instance()
        self.telegram = TelegramPoster()

        try:
            # Look for tokens in data folder
            token_path = 'data/instrument_tokens.json'
            if os.path.exists(token_path):
                with open(token_path, 'r') as f:
                    self.tokens = json.load(f)
            else:
                self.tokens = {}
                logger.warning("⚠️ instrument_tokens.json not found")
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
            self.tokens = {}

    def analyze_vsa_and_box(self, df):
        if df is None or len(df) < 30:
            return None

        recent_high = df['high'].iloc[-20:-1].max()
        recent_low = df['low'].iloc[-20:-1].min()
        current_close = df['close'].iloc[-1]
        current_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].iloc[-20:].mean()

        # Added safety for zero division
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0

        if current_close > recent_high and current_vol > (avg_vol * 1.5):
            return f"📦 BOX BREAKOUT above {recent_high}"

        if current_close < recent_low and current_vol > (avg_vol * 1.5):
            return f"⚠️ BOX BREAKDOWN below {recent_low}"

        if vol_ratio > 2.5:
            return f"🚀 VOLUME SPIKE ({round(vol_ratio, 1)}x)"

        return None

    def run(self):
        """Main execution logic for Currency signals"""
        if not self.kite:
            logger.error("❌ Currency Agent: Kite not available. Ensure access token is valid.")
            return

        # Changed to log instead of sending 'Started' message every 30 mins to avoid spam
        logger.info("💱 Currency Scan Started")

        # Current April Futures for USD, EUR, GBP
        targets = [
            "CDS:USDINR26APRFUT",
            "CDS:EURINR26APRFUT",
            "CDS:GBPINR26APRFUT"
        ]

        found_patterns = 0

        for symbol in targets:
            token = self.tokens.get(symbol)
            if not token:
                logger.debug(f"Token not found for {symbol}")
                continue

            try:
                # Fetch 7 days of 30-minute candles
                data = self.kite.historical_data(
                    token,
                    datetime.now() - timedelta(days=7),
                    datetime.now(),
                    "30minute"
                )

                if not data:
                    continue

                df = pd.DataFrame(data)
                pattern = self.analyze_vsa_and_box(df)

                if pattern:
                    msg = f"💱 *Currency Alert: {symbol}*\n{pattern}\nPrice: {df['close'].iloc[-1]}"
                    # Sending to 'free' channel as per your original logic
                    self.telegram.send_message("free", msg)
                    found_patterns += 1

            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        
        if found_patterns == 0:
            logger.info("🔍 Currency Scan: No patterns detected.")
