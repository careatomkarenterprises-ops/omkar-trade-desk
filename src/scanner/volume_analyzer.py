import pandas as pd

class VolumeSetupAnalyzer:
    def __init__(self, volume_period=15, min_candles=5, sma_period=15):
        self.volume_period = volume_period
        self.min_candles = min_candles
        self.sma_period = sma_period

    def detect_setups(self, df):
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
            setups.append({
                'top': top,
                'bottom': bottom,
                'range': range_size,
                'candles': len(block),
                'fab_50': top + range_size * 0.5  # primary target for long
            })
        return setups

    def check_sma_crossover(self, df):
        df['sma15'] = df['close'].rolling(self.sma_period).mean()
        df['above_sma'] = df['close'] > df['sma15']
        cross = df['above_sma'] != df['above_sma'].shift()
        return cross.iloc[-1]  # True if crossover just happened
