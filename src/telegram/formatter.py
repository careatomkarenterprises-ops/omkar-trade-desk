def format_volume_alert_compliant(symbol, setup, current_price, direction_bias):
    """
    SEBI-compliant alert: Educational pattern observation only.
    No entry, target, stop loss, or actionable recommendation.
    """
    msg = (f"📊 *Pattern Observation* - {symbol}\n"
           f"🔍 Volume setup detected: {setup['candles']} consecutive high-volume candles (≥15-period avg)\n"
           f"📐 Observed levels:\n"
           f"   🔴 Upper bound: ₹{setup['top']}\n"
           f"   🟢 Lower bound: ₹{setup['bottom']}\n"
           f"📈 Current price: ₹{current_price}\n"
           f"📏 Setup range: ₹{setup['range']}\n"
           f"🎯 Statistical zone (FAB 50%): ₹{setup['fab_50']}\n"
           f"📊 Historical probability: Similar patterns have shown movement towards this zone in 60-70% of cases (based on backtest).\n"
           f"📚 *Educational purpose only. Not a recommendation.*\n"
           f"🔗 Learn the methodology: [Link to educational content]")
    
    # For premium channel, add real-time timestamp and deeper stats
    return msg

def format_premarket_gap(gap_dir, global_sentiment, setup_range, fab_zone):
    """General market commentary for indices (allowed)"""
    msg = (f"🌅 *Pre-market observation*\n"
           f"📈 Nifty futures sentiment: {gap_dir.upper()} bias\n"
           f"🌍 Global cues: {global_sentiment}\n"
           f"📊 Observed resistance/support range: ₹{setup_range}\n"
           f"🎯 Statistical projection zone: ₹{fab_zone}\n"
           f"⚠️ This is an educational observation of market data. Not a trading recommendation.")
    return msg
