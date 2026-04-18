def format_volume_alert(symbol, signal_type, entry, target, stop, setup):
    """Formats volume setup alert with horizontal lines and FAB levels"""
    msg = (f"📊 *VOLUME SETUP ALERT* - {symbol}\n"
           f"🔹 Signal: {signal_type}\n"
           f"📊 Setup candles: {setup['candles']} (≥5)\n"
           f"🔴 Resistance (top): ₹{setup['top']}\n"
           f"🟢 Support (bottom): ₹{setup['bottom']}\n"
           f"💰 Entry: ₹{entry}\n"
           f"🎯 Primary target (50%): ₹{target}\n"
           f"🛑 Stop loss: ₹{stop}\n"
           f"🚀 FAB extensions: {setup['fab_127']} | {setup['fab_162']} | {setup['fab_200']}\n"
           f"📐 Range: ₹{setup['range']}")
    return msg
