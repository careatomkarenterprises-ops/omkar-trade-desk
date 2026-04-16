"""
Hedge Fund Options Intelligence Engine
NIFTY / BANKNIFTY Institutional Options Flow Detector
"""

import logging
import pandas as pd

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

                if momentum > 0:
                    score += 0.5
                else:
                    score -= 0.5

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
            step = 50
            atm = round(spot_price / step) * step

            if bias > 0:
                return {
                    "direction": "CALL SIDE",
                    "atm": atm,
                    "preferred_strikes": [atm, atm + step, atm + 2 * step]
                }

            else:
                return {
                    "direction": "PUT SIDE",
                    "atm": atm,
                    "preferred_strikes": [atm, atm - step, atm - 2 * step]
                }

        except Exception as e:
            logger.error(f"Strike selection error: {e}")
            return {}

    # -------------------------
    # OPTION FLOW ENGINE (NEW)
    # -------------------------
    def integrate_option_flow(self, call_oi, put_oi, call_vol, put_vol):

        try:
            oi_ratio = put_oi / call_oi if call_oi > 0 else 0
            vol_ratio = put_vol / call_vol if call_vol > 0 else 0

            signal = "NEUTRAL"
            strength = 0

            if oi_ratio > 1.2 and vol_ratio > 1.1:
                signal = "BULLISH ACCUMULATION (PUT WRITING)"
                strength += 0.7

            elif oi_ratio < 0.8 and vol_ratio < 0.9:
                signal = "BEARISH BUILDUP (CALL WRITING)"
                strength += 0.7

            else:
                strength += 0.3

            return {
                "oi_ratio": round(oi_ratio, 2),
                "vol_ratio": round(vol_ratio, 2),
                "signal": signal,
                "strength": round(strength, 2)
            }

        except Exception as e:
            logger.error(f"Option flow error: {e}")
            return {"signal": "UNKNOWN", "strength": 0}

    # -------------------------
    # FINAL INTELLIGENCE ENGINE
    # -------------------------
    def generate_options_signal(self, nifty_data, banknifty_data,
                                call_oi=0, put_oi=0, call_vol=0, put_vol=0):

        bias = self.detect_market_bias(nifty_data, banknifty_data)

        spot = 0
        try:
            spot = nifty_data["close"].iloc[-1]
        except:
            pass

        strike_data = self.select_strike_zone(spot, bias["overall_bias"])

        flow = self.integrate_option_flow(call_oi, put_oi, call_vol, put_vol)

        confidence = (
            abs(bias["overall_bias"]) * 40 +
            flow["strength"] * 40 +
            (1 if bias["overall_bias"] != 0 else 0) * 20
        )

        return {
            "bias": bias,
            "strike_plan": strike_data,
            "flow": flow,
            "confidence": min(confidence, 100),
            "market_type": "OPTIONS INSTITUTIONAL FLOW ENGINE"
        }
