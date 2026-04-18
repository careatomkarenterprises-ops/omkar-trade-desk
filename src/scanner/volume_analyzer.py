import pandas as pd

class VolumeSetupAnalyzer:
    def __init__(self, volume_period=15, min_candles=5, sma_period=15):
        self.volume_period = volume_period
        self.min_candles = min_candles
        self.sma_period = sma_period

    def detect_setups(self, df):
        if df is None or len(df) < self.min_candles + self.volume_period:
            return []
        df = df.copy()
        df['avg_volume'] = df['volume'].rolling(self.volume_period).mean()
        df['high_volume'] = df['volume'] > df['avg_volume']
        df['setup_group'] = (df['high_volume'] != df['high_volume'].shift()).cumsum()
        setup_lengths = df[df['high_volume']].groupby('setup_group').size()
        valid_groups = setup_lengths[setup_lengths >= self.min_candles].index
        setups = []
        for group in valid_groups:
            block = df[df['setup_group'] == group]
            top = block['high'].max()
            bottom = block['low'].min()
            range_size = top - bottom
            if range_size <= 0:
                continue
            fab_50 = top + range_size * 0.5
            setups.append({
                'top': round(top, 2),
                'bottom': round(bottom, 2),
                'range': round(range_size, 2),
                'candles': len(block),
                'fab_50': round(fab_50, 2)
            })
        return setups

    def check_sma_crossover(self, df):
        if len(df) < self.sma_period + 1:
            return False
        df['sma15'] = df['close'].rolling(self.sma_period).mean()
        df['above_sma'] = df['close'] > df['sma15']
        if len(df) >= 2:
            return df['above_sma'].iloc[-1] != df['above_sma'].iloc[-2]
        return False
