import logging

logger = logging.getLogger(__name__)

class PatternDetector:
    def analyze(self, symbol, df):
        try:
            if df is None or len(df) < 15:
                return {"symbol": symbol, "has_pattern": False}

            # 1. Check Trend (Price higher than 5 days ago)
            current_close = df["close"].iloc[-1]
            prev_close = df["close"].iloc[-5]
            trend = "UPTREND" if current_close > prev_close else "DOWNTREND"

            # 2. Volume Shock (Volume 1.5x higher than 10-day average)
            avg_volume = df["volume"].iloc[-11:-1].mean()
            current_volume = df["volume"].iloc[-1]
            volume_spike = current_volume > (avg_volume * 1.5)

            # 3. Breakout Logic
            # Closing above the high of the last 5 days
            recent_high = df["high"].iloc[-6:-1].max()
            breakout = current_close > recent_high
            
            # Closing below the low of the last 5 days
            recent_low = df["low"].iloc[-6:-1].min()
            breakdown = current_close < recent_low

            signal = None
            if trend == "UPTREND" and volume_spike and breakout:
                signal = "BUY_SIGNAL"
            elif trend == "DOWNTREND" and volume_spike and breakdown:
                signal = "SELL_SIGNAL"

            return {
                "symbol": symbol,
                "trend": trend,
                "signal": signal,
                "has_pattern": signal is not None,
                "price": round(current_close, 2)
            }

        except Exception as e:
            logger.error(f"Pattern error {symbol}: {e}")
            return {"symbol": symbol, "has_pattern": False}
