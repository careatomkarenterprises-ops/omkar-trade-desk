from src.telegram.poster import send_message


def route_signal(signal):

    if not signal:
        return

    # BASIC ROUTING LOGIC (KEEP SIMPLE)
    if signal.get("type") == "intraday":
        send_message("intraday", format_signal(signal))

    elif signal.get("type") == "premium":
        send_message("premium", format_signal(signal))

    else:
        send_message("free", format_signal(signal))


def format_signal(signal):

    return (
        f"📊 SIGNAL ALERT\n\n"
        f"Symbol: {signal.get('symbol')}\n"
        f"Signal: {signal.get('signal')}\n"
        f"Trend: {signal.get('trend')}\n"
    )
