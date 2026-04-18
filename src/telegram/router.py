from src.telegram.poster import send_message


def route_signal(signal):

    message = format_signal(signal)

    confidence = signal.get("confidence", 0)

    if confidence >= 80:
        send_message("premium_intraday", message)

    elif confidence >= 60:
        send_message("free_channel", message)


def format_signal(signal):

    return f"""
📊 {signal.get('symbol', 'N/A')}

Setup: {signal.get('pattern', 'N/A')}
Entry: {signal.get('entry', 'N/A')}
SL: {signal.get('sl', 'N/A')}
Target: {signal.get('target', 'N/A')}

🔥 Confidence: {signal.get('confidence')}%

Market Bias: {signal.get('market_bias')}

#OmkarTradeDesk
"""
