import pandas as pd
import logging

logger = logging.getLogger(__name__)


class PatternDetector:

    def analyze(self, symbol: str, df: pd.DataFrame):

        try:
            if df is None or df.empty:
                return None

            # ✅ FORCE LOWERCASE COLUMNS
            df.columns = [col.lower() for col in df.columns]

            # ✅ DEBUG (VERY IMPORTANT)
            logger.info(f"{symbol} columns: {df.columns.tolist()}")

            # ✅ USE LOWERCASE ONLY
            close = df["close"]
            high = df["high"]
            low = df["low"]
            volume = df["volume"]

            # -------------------------------
            # YOUR LOGIC
            # -------------------------------

            recent = df.tail(15)

            resistance = recent["high"].max()
            support = recent["low"].min()

            avg_volume = recent["volume"].mean()

            last_close = close.iloc[-1]
            last_volume = volume.iloc[-1]

            # PRE-BREAKOUT CONDITIONS
            near_resistance = (resistance - last_close) / resistance <= 0.005
            near_support = (last_close - support) / support <= 0.005

            low_volume = last_volume <= (avg_volume * 0.6)

            sustained_up = close.iloc[-1] > close.iloc[-2] > close.iloc[-3]
            sustained_down = close.iloc[-1] < close.iloc[-2] < close.iloc[-3]

            if near_resistance and low_volume and sustained_up:
                return {
                    "signal": "PRE_BREAKOUT_BUY",
                    "trend": "UPTREND"
                }

            elif near_support and low_volume and sustained_down:
                return {
                    "signal": "PRE_BREAKOUT_SELL",
                    "trend": "DOWNTREND"
                }

            return None

        except Exception as e:
            logger.error(f"Pattern error: {e}")
            return None
