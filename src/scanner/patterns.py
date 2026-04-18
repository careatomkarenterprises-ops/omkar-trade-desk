import pandas as pd
import numpy as np


class PatternDetector:

    def analyze(self, symbol, df: pd.DataFrame):

        if df is None or len(df) < 25:
            return None

        try:
            df = df.copy()

            # ============================
            # 🔹 MOVING AVERAGE
            # ============================
            df["SMA15"] = df["Close"].rolling(15).mean()

            recent = df.tail(10)

            # ============================
            # 🔹 RANGE DETECTION (5-6 candles)
            # ============================
            range_high = recent["High"].max()
            range_low = recent["Low"].min()
            range_size = range_high - range_low

            avg_price = recent["Close"].mean()

            # Tight range condition (compression)
            if range_size / avg_price > 0.025:  # >2.5% = no compression
                return None

            # ============================
            # 🔹 VOLUME ANALYSIS
            # ============================
            avg_volume = recent["Volume"].mean()
            last_volume = df.iloc[-1]["Volume"]

            volume_ok = (
                0.3 * avg_volume <= last_volume <= 0.6 * avg_volume
            )

            # ============================
            # 🔹 CURRENT PRICE
            # ============================
            last_close = df.iloc[-1]["Close"]

            # ============================
            # 🔹 TREND CHECK (SMA BASED)
            # ============================
            sma = df.iloc[-1]["SMA15"]

            if last_close > sma:
                trend = "UPTREND"
            elif last_close < sma:
                trend = "DOWNTREND"
            else:
                trend = "SIDEWAYS"

            # ============================
            # 🔥 PRE-BREAKOUT LOGIC (MAIN EDGE)
            # ============================

            proximity_high = abs(last_close - range_high) / range_high
            proximity_low = abs(last_close - range_low) / range_low

            near_high = proximity_high < 0.005   # within 0.5%
            near_low = proximity_low < 0.005

            # Last 3 candle stability
            last3 = df.tail(3)
            stable_high = all(last3["Close"] > (range_high * 0.995))
            stable_low = all(last3["Close"] < (range_low * 1.005))

            # ============================
            # 🔹 FINAL SIGNAL LOGIC
            # ============================

            # 🚀 PRE-BREAKOUT BUY
            if trend == "UPTREND" and near_high and stable_high and volume_ok:
                return {
                    "symbol": symbol,
                    "signal": "PRE_BREAKOUT_BUY",
                    "trend": trend,
                    "volume_spike": False
                }

            # 🔻 PRE-BREAKOUT SELL
            if trend == "DOWNTREND" and near_low and stable_low and volume_ok:
                return {
                    "symbol": symbol,
                    "signal": "PRE_BREAKOUT_SELL",
                    "trend": trend,
                    "volume_spike": False
                }

            # ============================
            # 🔥 CONFIRM BREAKOUT (OPTIONAL)
            # ============================

            if last_close > range_high and volume_ok:
                return {
                    "symbol": symbol,
                    "signal": "BREAKOUT_BUY",
                    "trend": trend,
                    "volume_spike": True
                }

            if last_close < range_low and volume_ok:
                return {
                    "symbol": symbol,
                    "signal": "BREAKOUT_SELL",
                    "trend": trend,
                    "volume_spike": True
                }

            return None

        except Exception as e:
            print(f"Pattern error {symbol}: {e}")
            return None
