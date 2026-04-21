import pandas as pd

class VolumeSetupAnalyzer:

    def __init__(self, volume_period=15, min_candles=5, sma_period=15):
        self.volume_period = volume_period
        self.min_candles = min_candles
        self.sma_period = sma_period

    # ============================
    # EXISTING LOGIC (UNCHANGED)
    # ============================
    def detect_setups(self, df):

        try:
            if df is None or df.empty or len(df) < self.volume_period:
                return []

            df = df.copy()

            df['avg_volume'] = df['volume'].rolling(self.volume_period).mean()

            df = df.dropna().reset_index(drop=True)

            if len(df) < self.volume_period:
                return []

            df['high_volume'] = (df['volume'].values > df['avg_volume'].values)

            setups = []
            count = 0

            for i in range(len(df)):

                if df['high_volume'].iloc[i]:
                    count += 1
                else:
                    if count >= self.min_candles:

                        window = df.iloc[i-count:i]

                        setups.append({
                            "candles": count,
                            "top": float(window['high'].max()),
                            "bottom": float(window['low'].min()),
                            "range": float(window['high'].max() - window['low'].min()),
                            "fab_50": float((window['high'].max() + window['low'].min()) / 2)
                        })

                    count = 0

            return setups

        except Exception as e:
            print(f"Analyzer error: {e}")
            return []

    # ============================
    # SMA (UNCHANGED)
    # ============================
    def check_sma_crossover(self, df):

        try:
            if df is None or len(df) < self.sma_period:
                return False

            df = df.copy()

            df['sma'] = df['close'].rolling(self.sma_period).mean()

            if pd.isna(df['sma'].iloc[-1]):
                return False

            return df['close'].iloc[-1] > df['sma'].iloc[-1]

        except Exception as e:
            print(f"SMA error: {e}")
            return False

    # ============================
    # 🧠 NEW: SMART MONEY ENGINE
    # ============================
    def smart_money_score(self, df):

        try:
            if df is None or df.empty or len(df) < self.volume_period:
                return 0, "NO DATA"

            df = df.copy()

            df['avg_volume'] = df['volume'].rolling(self.volume_period).mean()
            df = df.dropna()

            if df.empty:
                return 0, "NO DATA"

            # Volume pressure
            volume_ratio = len(df[df['volume'] > df['avg_volume']]) / len(df)

            # Trend strength
            price_change = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]

            # Smart money score
            score = (volume_ratio * 60) + (price_change * 100)

            score = max(0, min(100, score * 50))

            if score >= 75:
                return score, "STRONG ACCUMULATION 🔥"
            elif score >= 55:
                return score, "MODERATE ACCUMULATION"
            elif score >= 35:
                return score, "WEAK INTEREST"
            else:
                return score, "NO SMART MONEY"

        except Exception as e:
            print(f"Smart money error: {e}")
            return 0, "ERROR"
