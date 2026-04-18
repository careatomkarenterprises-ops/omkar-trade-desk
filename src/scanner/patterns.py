import pandas as pd
import logging

logger = logging.getLogger(__name__)


class PatternDetector:

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert all column names to lowercase
        So no case mismatch ever again
        """
        df.columns = [col.lower() for col in df.columns]
        return df

    def analyze(self, symbol: str, df: pd.DataFrame):

        try:
            if df is None or df.empty:
                return None

            # ✅ FIX: normalize column names
            df = self.normalize_columns(df)

            # Now ALWAYS use lowercase
            close = df["close"]
            high = df["high"]
            low = df["low"]
            volume = df["volume"]

            # -------------------------------
            # 📊 YOUR LOGIC STARTS HERE
            # -------------------------------

            # 15 candle range
            recent = df.tail(15)

            resistance = recent["high"].max()
            support = recent["low"].min()

            avg_volume = recent["volume"].mean()

            last_close = close.iloc[-1]
            prev_close = close.iloc[-2]
            last_volume = volume.iloc[-1]

            # -----------------------------------
            # 🔥 PRE-BREAKOUT LOGIC (YOUR IDEA)
            # -----------------------------------

            near_resistance = (resistance - last_close) / resistance <= 0.005
            near_support = (last_close - support) / support <= 0.005

            low_volume = last_volume <= (avg_volume * 0.6)

            sustained_up = (
                close.iloc[-1] > close.iloc[-2] > close.iloc[-3]
            )

            sustained_down = (
                close.iloc[-1] < close.iloc[-2] < close.iloc[-3]
            )

            # -----------------------------------
            # 🚀 SIGNAL GENERATION
            # -----------------------------------

            if near_resistance and low_volume and sustained_up:
                return {
                    "signal": "PRE_BREAKOUT_BUY",
                    "trend": "UPTREND",
                    "volume_spike": False
                }

            elif near_support and low_volume and sustained_down:
                return {
                    "signal": "PRE_BREAKOUT_SELL",
                    "trend": "DOWNTREND",
                    "volume_spike": False
                }

            return None

        except Exception as e:
            logger.error(f"Pattern error: {e}")
            return None
