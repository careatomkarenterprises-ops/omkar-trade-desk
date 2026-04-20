import requests
import os
from datetime import datetime, timedelta
from kiteconnect import KiteConnect

# ============================
# ENV VARIABLES
# ============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

CHANNELS = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

# ============================
# INIT KITE
# ============================
kite = KiteConnect(api_key=KITE_API_KEY)
kite.set_access_token(KITE_ACCESS_TOKEN)

# Instrument Tokens
NIFTY_TOKEN = 256265
BANKNIFTY_TOKEN = 260105

# ============================
# TELEGRAM
# ============================
def send_telegram(message):
    if not BOT_TOKEN:
        print("❌ Missing TELEGRAM_BOT_TOKEN")
        return

    for channel in CHANNELS:
        if not channel:
            continue

        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": channel,
                "text": message,
                "parse_mode": "Markdown"
            }

            res = requests.post(url, data=payload, timeout=10)

            if res.status_code == 200:
                print(f"✅ Sent to {channel}")
            else:
                print(f"❌ Failed {channel}: {res.text}")

        except Exception as e:
            print(f"❌ Telegram Error: {e}")

# ============================
# INDEX DATA (ZERODHA)
# ============================
def get_index_data(token):
    try:
        to_date = datetime.now().date()
        from_date = to_date - timedelta(days=5)

        data = kite.historical_data(
            token,
            from_date=from_date,
            to_date=to_date,
            interval="day"
        )

        if len(data) < 2:
            print("❌ Not enough data")
            return None

        prev = data[-2]
        current = data[-1]

        prev_close = prev["close"]
        high = prev["high"]
        low = prev["low"]

        change = ((current["close"] - prev_close) / prev_close) * 100

        return {
            "prev_close": prev_close,
            "high": high,
            "low": low,
            "change": change
        }

    except Exception as e:
        print("❌ Kite Error:", e)
        return None

# ============================
# SIMPLE GLOBAL SENTIMENT (STATIC SAFE)
# ============================
def get_global_sentiment():
    # Since global APIs fail, use neutral base
    return "NEUTRAL", 1

# ============================
# LOGIC
# ============================
def get_bias(change):
    if change > 0.4:
        return "BULLISH"
    elif change < -0.4:
        return "BEARISH"
    return "SIDEWAYS"

def get_opening_range(prev_close, high, low):
    range_size = high - low
    low_range = prev_close - (range_size * 0.25)
    high_range = prev_close + (range_size * 0.25)
    return round(low_range), round(high_range), range_size

def get_volatility(range_size):
    if range_size > 350:
        return "HIGH"
    elif range_size > 180:
        return "NORMAL"
    return "LOW"

def get_confidence(score, bias):
    if score >= 2 and bias == "BULLISH":
        return "HIGH"
    elif score == 0 and bias == "BEARISH":
        return "HIGH"
    elif score == 1:
        return "MEDIUM"
    return "LOW"

def get_behavior(sentiment, bias):
    if "BULLISH" in sentiment and bias == "BULLISH":
        return "Trend Up Day"
    elif "BEARISH" in sentiment and bias == "BEARISH":
        return "Trend Down Day"
    elif bias == "SIDEWAYS":
        return "Range-bound"
    return "Volatile / Uncertain"

# ============================
# MESSAGE
# ============================
def create_message(sentiment, score, nifty, banknifty):
    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(banknifty["change"])

    n_low, n_high, n_range = get_opening_range(
        nifty["prev_close"], nifty["high"], nifty["low"]
    )
    b_low, b_high, b_range = get_opening_range(
        banknifty["prev_close"], banknifty["high"], banknifty["low"]
    )

    volatility = get_volatility(n_range)
    confidence = get_confidence(score, nifty_bias)
    behavior = get_behavior(sentiment, nifty_bias)

    msg = "🌅 *PRE-MARKET INDEX INTELLIGENCE*\n\n"

    msg += f"🌍 Global Sentiment: *{sentiment}*\n\n"

    msg += "📊 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{bank_bias}*\n\n"

    msg += "📍 Expected Opening Zone:\n"
    msg += f"• NIFTY: {n_low} – {n_high}\n"
    msg += f"• BANK NIFTY: {b_low} – {b_high}\n\n"

    msg += f"⚡ Volatility: *{volatility}*\n\n"
    msg += f"🎯 Confidence: *{confidence}*\n\n"

    msg += "📦 Market Behaviour:\n"
    msg += f"• {behavior}\n"
    msg += "• Wait for confirmation after 9:20 AM\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    msg += "\n\n⚠️ Informational only. Not financial advice."

    return msg

# ============================
# FALLBACK
# ============================
def fallback_message():
    return (
        "⚠️ *Pre-Market Update*\n\n"
        "Data temporarily unavailable.\n"
        "Market view will be shared after open.\n\n"
        "⏰ " + datetime.now().strftime('%H:%M:%S')
    )

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        print("🚀 Running Zerodha Market Predictor...")

        sentiment, score = get_global_sentiment()

        nifty = get_index_data(NIFTY_TOKEN)
        banknifty = get_index_data(BANKNIFTY_TOKEN)

        if not nifty or not banknifty:
            print("❌ Data missing → sending fallback")
            send_telegram(fallback_message())
        else:
            message = create_message(sentiment, score, nifty, banknifty)
            print(message)
            send_telegram(message)

        print("✅ Done")

    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        send_telegram(fallback_message())
