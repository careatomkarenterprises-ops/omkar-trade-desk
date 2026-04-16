"""
Hedge Fund Options Intelligence Engine
NIFTY / BANKNIFTY Institutional Options Flow Detector
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class OptionsIntelligenceEngine:

    def __init__(self):
        self.volatility_window = 20
        self.oi_threshold = 1.3

    # -------------------------
    # MARKET BIAS ENGINE
    # -------------------------
    def detect_market_bias(self, nifty_data, banknifty_data):

        try:
            def compute_bias(data):
                if data is None or data.empty:
                    return 0

                data = data.copy()
                data["returns"] = data["close"].pct_change()

                momentum = data["returns"].rolling(5).mean().iloc[-1]
                volatility = data["returns"].rolling(10).std().iloc[-1]

                score = 0

                # Momentum bias
                if momentum > 0:
                    score += 0.5
                else:
                    score -= 0.5

                # Volatility expansion = trend day
                if volatility > data["returns"].std():
                    score += 0.5

                return round(score, 2)

            nifty_bias = compute_bias(nifty_data)
            banknifty_bias = compute_bias(banknifty_data)

            overall_bias = (nifty_bias + banknifty_bias) / 2

            return {
                "nifty_bias": nifty_bias,
                "banknifty_bias": banknifty_bias,
                "overall_bias": round(overall_bias, 2)
            }

        except Exception as e:
            logger.error(f"Market bias error: {e}")
            return {"overall_bias": 0}

    # -------------------------
    # STRIKE SELECTION ENGINE
    # -------------------------
    def select_strike_zone(self, spot_price, bias):

        try:
            step = 50  # simplified strike interval

            atm = round(spot_price / step) * step

            if bias > 0:
                # bullish
                return {
                    "direction": "CALL SIDE",
                    "atm": atm,
                    "preferred_strikes": [atm, atm + step, atm + 2 * step]
                }

            else:
                # bearish
                return {
                    "direction": "PUT SIDE",
                    "atm": atm,
                    "preferred_strikes": [atm, atm - step, atm - 2 * step]
                }

        except Exception as e:
            logger.error(f"Strike selection error: {e}")
            return {}

    # -------------------------
    # FINAL INTELLIGENCE ENGINE
    # -------------------------
    def generate_options_signal(self, nifty_data, banknifty_data):

        bias = self.detect_market_bias(nifty_data, banknifty_data)

        spot = 0
        try:
            spot = nifty_data["close"].iloc[-1]
        except:
            pass

        strike_data = self.select_strike_zone(spot, bias["overall_bias"])

        return {
            "bias": bias,
            "strike_plan": strike_data,
            "confidence": min(abs(bias["overall_bias"]) * 100, 100)
        }
