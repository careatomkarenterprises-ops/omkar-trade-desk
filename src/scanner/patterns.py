import pandas as pd
import numpy as np


class PatternDetector:

    def analyze(self, symbol, df: pd.DataFrame):

        if df is None or len(df) < 25:
            return None

        try:
            df = df.copy()

            # ============================
            # 🔥 FIX: STANDARDIZE COLUMNS
            # ============================
            df.columns = [c.capitalize() for c in df.columns]

            required_cols = ["Open", "High", "Low", "Close", "Volume"]

            for col in required_cols:
                if col not in df.columns:
                    return None

            # ============================
            # 🔹 MOVING AVERAGE
            # ============================
            df["SMA15"] = df["Close"].rolling(15).mean()

            recent = df.tail(10)

            # ============================
            # 🔹 RANGE DETECTION
            # ============================
            range_high = recent["High"].max()
            range_low = recent["Low"].min()
            range_size = range_high - range_low

            avg_price = recent["Close"].mean()

            # Compression filter
            if range_size / avg_price > 0.025:
                return None

            # ============================
            # 🔹 VOLUME LOGIC
            # ============================
            avg_volume = recent["Volume"].mean()
            last_volume = df.iloc[-1]["Volume"]

            volume_ok = 0.3 * avg_volume <= last_volume <= 0.6 * avg_volume

            # ============================
            # 🔹 PRICE
            # ============================
            last_close = df.iloc[-1]["Close"]

            # ============================
            # 🔹 TREND
            # ============================
            sma = df.iloc[-1]["SMA15"]

            if last_close > sma:
                trend = "UPTREND"
            elif last_close < sma:
                trend = "DOWNTREND"
            else:
                trend = "SIDEWAYS"

            # ============================
            # 🔥 PRE-BREAKOUT LOGIC
            # ============================
            proximity_high = abs(last_close - range_high) / range_high
            proximity_low = abs(last_close - range_low) / range_low

            near_high = proximity_high < 0.005
            near_low = proximity_low < 0.005

            last3 = df.tail(3)

            stable_high = all(last3["Close"] > (range_high * 0.995))
            stable_low = all(last3["Close"] < (range_low * 1.005))

            # ============================
            # 🚀 SIGNALS
            # ============================

            if trend == "UPTREND" and near_high and stable_high and volume_ok:
                return {
                    "symbol": symbol,
                    "signal": "PRE_BREAKOUT_BUY",
                    "trend": trend,
                    "volume_spike": False
                }

            if trend == "DOWNTREND" and near_low and stable_low and volume_ok:
                return {
                    "symbol": symbol,
                    "signal": "PRE_BREAKOUT_SELL",
                    "trend": trend,
                    "volume_spike": False
                }

            # Breakout confirmation (optional)
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
            print(f"Pattern error: {e}")
            return None
