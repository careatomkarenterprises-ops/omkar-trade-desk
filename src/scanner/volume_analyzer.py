import pandas as pd
import numpy as np

class VolumeSetupAnalyzer:
    def __init__(self, volume_period=15, min_candles=5, sma_period=15):
        self.volume_period = volume_period
        self.min_candles = min_candles
        self.sma_period = sma_period

    def detect_setups(self, df):
        """df must have columns: 'high', 'low', 'close', 'volume'"""
        df = df.copy()
        
        # 1. Volume > 15-period average
        df['avg_volume'] = df['volume'].rolling(self.volume_period).mean()
        df['high_volume'] = df['volume'] > df['avg_volume']
        
        # 2. Find consecutive runs of high_volume (min 5)
        df['setup_group'] = (df['high_volume'] != df['high_volume'].shift()).cumsum()
        setup_lengths = df[df['high_volume']].groupby('setup_group').size()
        valid_groups = setup_lengths[setup_lengths >= self.min_candles].index
        
        # 3. For each valid setup, get horizontal lines & FAB levels
        setups = []
        for group in valid_groups:
            block = df[df['setup_group'] == group]
            top = block['high'].max()
            bottom = block['low'].min()
            range_size = top - bottom
            # FAB extension levels (primary target = 50% of range)
            target_50 = top + (range_size * 0.5) if 'breakout_above' else bottom - (range_size * 0.5)
            fab_levels = {
                '50%': target_50,
                'ext1': top + range_size * 1.272,
                'ext2': top + range_size * 1.618,
                'ext3': top + range_size * 2.0
            }
            setups.append({
                'start_date': block.index[0],
                'end_date': block.index[-1],
                'top_resistance': top,
                'bottom_support': bottom,
                'range': range_size,
                'fab_targets': fab_levels,
                'setup_candles': len(block)
            })
        return setups

    def check_sma_crossover(self, df):
        """15-day SMA: back-to-back cross (price above then below or vice versa)"""
        df['sma15'] = df['close'].rolling(self.sma_period).mean()
        df['above_sma'] = df['close'] > df['sma15']
        # Detect change in above_sma (crossover)
        df['cross'] = df['above_sma'] != df['above_sma'].shift()
        cross_points = df[df['cross']].index.tolist()
        return cross_points, df['sma15'].iloc[-1]
