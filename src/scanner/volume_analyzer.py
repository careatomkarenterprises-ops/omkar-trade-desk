import pandas as pd

class VolumeSetupAnalyzer:
    def __init__(self, volume_period=15, min_candles=5, sma_period=15):
        self.volume_period = volume_period
        self.min_candles = min_candles
        self.sma_period = sma_period

    def detect_setups(self, df):
        try:
            if df is None or df.empty or len(df) < self.volume_period:
                return []

            df = df.copy()

            df['avg_volume'] = df['volume'].rolling(self.volume_period).mean()

            df = df.dropna().reset_index(drop=True)

            if df.empty:
                return []

            df['high_volume'] = df['volume'] > df['avg_volume']

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

    def check_sma_crossover(self, df):
        try:
            if df is None or len(df) < self.sma_period + 1:
                return False

            df = df.copy()

            df['sma'] = df['close'].rolling(self.sma_period).mean()

            if pd.isna(df['sma'].iloc[-1]):
                return False

            return df['close'].iloc[-1] > df['sma'].iloc[-1]

        except Exception as e:
            print(f"SMA error: {e}")
            return False
