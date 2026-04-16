"""
Pattern Detector - Production Stable Version
"""

import logging

logger = logging.getLogger(__name__)


class PatternDetector:

    def analyze(self, symbol, df):
        try:
            if df is None or len(df) < 10:
                return None

            trend = self._get_trend(df)
            volume_spike = self._check_volume(df)
            breakout = self._check_breakout(df)
            breakdown = self._check_breakdown(df)

            signal = None

            if trend == "UPTREND" and volume_spike and breakout:
                signal = "BUY_SIGNAL"

            elif trend == "DOWNTREND" and volume_spike and breakdown:
                signal = "SELL_SIGNAL"

            return {
                "symbol": symbol,
                "trend": trend,
                "signal": signal,
                "has_pattern": signal is not None
            }

        except Exception as e:
            logger.error(f"Pattern error {symbol}: {e}")
            return None

    # ---------------- INTERNAL LOGIC ----------------

    def _get_trend(self, df):
        try:
            return "UPTREND" if df["close"].iloc[-1] > df["close"].iloc[-5] else "DOWNTREND"
        except:
            return "SIDEWAYS"

    def _check_volume(self, df):
        try:
            return df["volume"].iloc[-1] > df["volume"].mean()
        except:
            return False

    def _check_breakout(self, df):
        try:
            return df["close"].iloc[-1] > df["high"].iloc[-5:].max()
        except:
            return False

    def _check_breakdown(self, df):
        try:
            return df["close"].iloc[-1] < df["low"].iloc[-5:].min()
        except:
            return False
