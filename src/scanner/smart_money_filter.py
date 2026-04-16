"""
Smart Money Filter - Institutional Accumulation Detector
Removes fake breakouts and low-quality signals
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SmartMoneyFilter:
    def __init__(self):
        self.volume_threshold = 1.5
        self.volatility_threshold = 2.0

    def is_institutional_move(self, data: pd.DataFrame) -> dict:
        """
        Detect institutional activity:
        - Volume expansion
        - Price compression breakout
        - Low volatility base
        """

        try:
            if len(data) < 20:
                return {"valid": False}

            df = data.copy()

            # Volume average
            df["vol_avg"] = df["volume"].rolling(20).mean()

            # Volatility (ATR-like simple version)
            df["range"] = df["high"] - df["low"]
            df["volatility"] = df["range"].rolling(20).mean()

            latest = df.iloc[-1]
            prev = df.iloc[-5:-1]

            # 1. Volume expansion
            volume_spike = latest["volume"] > latest["vol_avg"] * self.volume_threshold

            # 2. Base formation (low volatility before breakout)
            low_volatility_base = prev["volatility"].mean() < latest["volatility"] * self.volatility_threshold

            # 3. Price expansion confirmation
            price_expansion = latest["range"] > df["range"].rolling(20).mean().iloc[-1]

            score = 0
            if volume_spike:
                score += 0.4
            if low_volatility_base:
                score += 0.3
            if price_expansion:
                score += 0.3

            return {
                "valid": score >= 0.6,
                "score": round(score, 2),
                "volume_spike": volume_spike,
                "low_volatility_base": low_volatility_base,
                "price_expansion": price_expansion
            }

        except Exception as e:
            logger.error(f"Smart Money Filter Error: {e}")
            return {"valid": False}
