"""
Omkar Trade Services - Swing Agent
Logic: VSA (Volume Spread Analysis) - Shakeouts & Supply Tests
"""
class SwingAgent:
    def __init__(self, kite_instance):
        self.kite = kite_instance

    def check_vsa_shakeout(self, symbol):
        """
        Detects a 'Shakeout':
        1. Price breaks a recent low.
        2. Closes back above it with HIGH volume.
        """
        # Fetch 30 days of daily candles
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        # Note: Replace with actual instrument_token
        candles = self.kite.historical_data(instrument_token, from_date, to_date, "day")
        df = pd.DataFrame(candles)
        
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        avg_volume = df['volume'].tail(20).mean()

        # VSA Logic: Shakeout
        is_shakeout = (last_candle['low'] < prev_candle['low']) and \
                      (last_candle['close'] > prev_candle['low']) and \
                      (last_candle['volume'] > 1.5 * avg_volume)
        
        return is_shakeout
