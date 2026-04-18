def format_volume_alert(stock, setup, direction, current_price):
    msg = f"📊 *{stock}* - Volume Setup Detected\n"
    msg += f"🔹 Setup candles: {setup['setup_candles']} (≥5)\n"
    msg += f"🔹 Resistance: ₹{setup['top_resistance']:.2f}\n"
    msg += f"🔹 Support: ₹{setup['bottom_support']:.2f}\n"
    msg += f"🔹 Current: ₹{current_price:.2f}\n"
    if direction == 'long':
        msg += f"✅ Breakout above resistance → Target 50%: ₹{setup['fab_targets']['50%']:.2f}\n"
        msg += f"🚀 Extensions: 1.272 | 1.618 | 2.0\n"
    else:
        msg += f"⬇️ Breakdown below support → Target -50%: ₹{setup['fab_targets']['50%']:.2f}\n"
    msg += f"🛑 Stop: ₹{setup['bottom_support'] - (setup['range']*0.25):.2f}\n"
    return msg
