"""
Pattern Detection Engine - Institutional Multi-Factor Breakout System (Upgraded)
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PatternDetector:
    def __init__(self):
        self.version = "4.0"

        # Core Parameters
        self.vol_sma_period = 15
        self.quiet_days = 6
        self.surge_threshold = 1.8

        # New Filters
        self.trend_period = 20
        self.fake_breakout_buffer = 0.15  # % buffer to avoid wick traps

    # ---------------- TREND FILTER ----------------
    def get_trend(self, data):
        try:
            ema = data['close'].ewm(span=self.trend_period).mean()
            return "UPTREND" if data['close'].iloc[-1] > ema.iloc[-1] else "DOWNTREND"
        except:
            return "UNKNOWN"

    # ---------------- VOLUME BOX BREAKOUT ----------------
    def detect_volume_price_box(self, data: pd.DataFrame) -> Dict:

        try:
            if len(data) < 25:
                return {'detected': False}

            data = data.copy()

            # Volume SMA
            data['vol_sma'] = data['volume'].rolling(self.vol_sma_period).mean()

            # Quiet zone
            quiet_slice = data.iloc[-(self.quiet_days + 1):-1]

            if len(quiet_slice) < self.quiet_days:
                return {'detected': False}

            is_quiet = all(quiet_slice['volume'] < quiet_slice['vol_sma'])

            resistance = quiet_slice['high'].max()
            support = quiet_slice['low'].min()

            current = data.iloc[-1]

            price = current['close']
            volume = current['volume']
            vol_sma = current['vol_sma']

            if pd.isna(vol_sma) or vol_sma == 0:
                return {'detected': False}

            # ---------------- CONDITIONS ----------------
            breakout = price > resistance * (1 + self.fake_breakout_buffer / 100)
            breakdown = price < support * (1 - self.fake_breakout_buffer / 100)

            volume_surge = volume > (vol_sma * self.surge_threshold)

            trend = self.get_trend(data)

            # Trend alignment filter
            trend_ok = True
            if breakout and trend != "UPTREND":
                trend_ok = False
            if breakdown and trend != "DOWNTREND":
                trend_ok = False

            # Final validation
            if (breakout or breakdown) and volume_surge and is_quiet and trend_ok:

                trigger_type = "🚀 BREAKOUT DETECTED" if breakout else "📉 BREAKDOWN DETECTED"
                surge_ratio = round(volume / vol_sma, 2)

                # ---------------- SCORING SYSTEM ----------------
                score = 0

                score += 40 if is_quiet else 0
                score += min(surge_ratio * 10, 30)
                score += 20 if trend_ok else 0
                score += 10 if volume_surge else 0

                score = min(score, 100)

                return {
                    'detected': True,
                    'trigger': trigger_type,
                    'resistance': round(resistance, 2),
                    'support': round(support, 2),
                    'surge_ratio': surge_ratio,
                    'trend': trend,
                    'strength': score / 100
                }

            return {'detected': False}

        except Exception as e:
            logger.error(f"Pattern Error: {e}")
            return {'detected': False}

    # ---------------- MAIN ENTRY ----------------
    def analyze(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:

        if data is None or data.empty:
            return None

        res = self.detect_volume_price_box(data)

        if res.get('detected'):

            return {
                'symbol': symbol,
                'price': round(data['close'].iloc[-1], 2),
                'has_pattern': True,
                'trigger': res['trigger'],
                'surge_ratio': res['surge_ratio'],
                'resistance': res['resistance'],
                'support': res['support'],
                'trend': res.get('trend', 'UNKNOWN'),
                'strength': res['strength']
            }

        return {'symbol': symbol, 'has_pattern': False}
