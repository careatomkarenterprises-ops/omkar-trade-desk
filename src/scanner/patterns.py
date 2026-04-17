import logging

logger = logging.getLogger(__name__)

class PatternDetector:
    def analyze(self, symbol, df):
        try:
            if df is None or len(df) < 20: # Need more data for stable moving averages
                return None

            trend = self._get_trend(df)
            volume_spike = self._check_volume(df)
            breakout = self._check_breakout(df)
            breakdown = self._check_breakdown(df)

            signal = None

            # BUY: Trend is up + Volume Shock + Price crossing High of last 5 days
            if trend == "UPTREND" and volume_spike and breakout:
                signal = "BUY_SIGNAL"

            # SELL: Trend is down + Volume Shock + Price crossing Low of last 5 days
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

    def _get_trend(self, df):
        try:
            # Short term 5-period trend
            return "UPTREND" if df["close"].iloc[-1] > df["close"].iloc[-5] else "DOWNTREND"
        except:
            return "SIDEWAYS"

    def _check_volume(self, df):
        try:
            # Volume Shock: Current volume > 1.5x the 10-day average volume
            avg_vol = df["volume"].iloc[-10:].mean()
            return df["volume"].iloc[-11] > (avg_vol * 1.5)
        except:
            return False

    def _check_breakout(self, df):
        try:
            # Price closes above the high of the previous 5 days
            return df["close"].iloc[-1] > df["high"].iloc[-6:-1].max()
        except:
            return False

    def _check_breakdown(self, df):
        try:
            # Price closes below the low of the previous 5 days
            return df["close"].iloc[-1] < df["low"].iloc[-6:-1].min()
        except:
            return False
