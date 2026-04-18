def predict_gap_with_volume_setup(self):
    """Predicts gap up/down using volume setup on 30-min pre-market data"""
    from src.scanner.volume_analyzer import VolumeSetupAnalyzer

    # Fetch 30-min data for NIFTY (last 5 days)
    df_30m = self.fetch_30min_data("NIFTY")
    if df_30m is None or df_30m.empty:
        return {"gap": "neutral", "reason": "No data"}

    analyzer = VolumeSetupAnalyzer()
    setups = analyzer.detect_setups(df_30m)
    if not setups:
        return {"gap": "neutral", "reason": "No volume setup found"}

    latest = setups[-1]
    current_price = self.get_current_futures_price()  # from Zerodha
    global_sentiment = self.get_global_sentiment()    # SGX Nifty, Dow Futures

    if current_price > latest['top']:
        gap_dir = "up"
        target = latest['fab_50']
        reason = f"Price above resistance {latest['top']}"
    elif current_price < latest['bottom']:
        gap_dir = "down"
        target = latest['bottom'] - latest['range'] * 0.5
        reason = f"Price below support {latest['bottom']}"
    else:
        return {"gap": "neutral", "reason": "Inside range"}

    # Build prediction message
    msg = (f"🌅 *PRE-MARKET GAP PREDICTION*\n"
           f"📈 Direction: {gap_dir.upper()}\n"
           f"🎯 Primary target: ₹{target}\n"
           f"📐 Setup range: ₹{latest['range']}\n"
           f"🌍 Global sentiment: {global_sentiment}\n"
           f"🔍 Reason: {reason}")
    send_alert(msg, channel="@OmkarFree")  # Free channel for trust building
    return {"gap": gap_dir, "target": target}
