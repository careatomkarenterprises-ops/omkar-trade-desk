def predict_gap_with_volume(self):
    # Fetch SGX Nifty, Dow Futures, Asian markets
    global_sentiment = self.get_global_sentiment()
    # Fetch index futures pre-market volume (Zerodha)
    futures_volume = self.get_futures_premarket_volume()
    # Run volume setup on 30-min chart (previous 5 days)
    df_30m = self.fetch_30min_data("NIFTY")
    analyzer = VolumeSetupAnalyzer()
    setups = analyzer.detect_setups(df_30m)
    latest_setup = setups[-1] if setups else None
    # If price is opening above top_resistance → gap up target = fab 50%
    # If below bottom_support → gap down target = -50%
    prediction = {
        'gap_direction': 'up' if current_price > latest_setup['top_resistance'] else 'down',
        'primary_target': latest_setup['fab_targets']['50%'],
        'confidence': 'high' if futures_volume > avg_volume * 1.5 else 'medium'
    }
    return prediction
