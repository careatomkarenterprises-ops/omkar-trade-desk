class FABTargetCalculator:
    @staticmethod
    def compute(setup_high, setup_low, direction='long'):
        range_size = setup_high - setup_low
        if direction == 'long':
            entry = setup_high  # breakout above resistance
            targets = {
                'target_1': entry + range_size * 0.5,   # 50% level
                'target_2': entry + range_size * 1.272,
                'target_3': entry + range_size * 1.618,
                'target_4': entry + range_size * 2.0,
                'stop_loss': setup_low - range_size * 0.25
            }
        else:  # short
            entry = setup_low   # breakdown below support
            targets = {
                'target_1': entry - range_size * 0.5,
                'target_2': entry - range_size * 1.272,
                'target_3': entry - range_size * 1.618,
                'target_4': entry - range_size * 2.0,
                'stop_loss': setup_high + range_size * 0.25
            }
        return targets
