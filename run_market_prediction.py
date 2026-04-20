import requests
import os
from datetime import datetime
import yfinance as yf

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNELS = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

# ============================
# TELEGRAM
# ============================
def send_telegram(message):
    for channel in CHANNELS:
        if not channel:
            continue

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": channel,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            requests.post(url, data=payload, timeout=10)
        except:
            continue

# ============================
# GLOBAL SENTIMENT
# ============================
def get_global_sentiment():
    try:
        dow = yf.Ticker("^DJI").history(period="1d")
        nasdaq = yf.Ticker("^IXIC").history(period="1d")
        sp500 = yf.Ticker("^GSPC").history(period="1d")

        score = 0

        if not dow.empty and dow["Close"].iloc[-1] > dow["Open"].iloc[-1]:
            score += 1
        if not nasdaq.empty and nasdaq["Close"].iloc[-1] > nasdaq["Open"].iloc[-1]:
            score += 1
        if not sp500.empty and sp500["Close"].iloc[-1] > sp500["Open"].iloc[-1]:
            score += 1

        if score >= 2:
            return "BULLISH"
        elif score == 1:
            return "MIXED"
        else:
            return "BEARISH"

    except:
        return "NEUTRAL"

# ============================
# INDEX DATA (NIFTY / BANKNIFTY)
# ============================
def get_index_data(symbol):
    try:
        df = yf.Ticker(symbol).history(period="2d")

        if len(df) < 2:
            return None

        prev = df.iloc[-2]
        current = df.iloc[-1]

        prev_close = prev["Close"]
        high = prev["High"]
        low = prev["Low"]

        change = ((current["Close"] - prev_close) / prev_close) * 100

        return {
            "prev_close": prev_close,
            "high": high,
            "low": low,
            "change": change
        }

    except:
        return None

# ============================
# BIAS
# ============================
def get_bias(change):
    if change > 0.3:
        return "BULLISH"
    elif change < -0.3:
        return "BEARISH"
    else:
        return "SIDEWAYS"

# ============================
# OPENING RANGE
# ============================
def get_opening_range(prev_close, high, low):
    range_size = high - low

    low_range = prev_close - (range_size * 0.25)
    high_range = prev_close + (range_size * 0.25)

    return round(low_range), round(high_range), range_size

# ============================
# VOLATILITY
# ============================
def get_volatility(range_size):
    if range_size > 300:
        return "HIGH"
    elif range_size > 150:
        return "NORMAL"
    else:
        return "LOW"

# ============================
# MARKET BEHAVIOR
# ============================
def get_behavior(sentiment, bias):
    if sentiment == "BULLISH" and bias == "BULLISH":
        return "Trend Up Day"
    elif sentiment == "BEARISH" and bias == "BEARISH":
        return "Trend Down Day"
    elif sentiment == "MIXED" and bias == "SIDEWAYS":
        return "Range-bound"
    else:
        return "Volatile / Uncertain"

# ============================
# MESSAGE
# ============================
def create_message(sentiment, nifty, banknifty):
    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(banknifty["change"])

    n_low, n_high, n_range = get_opening_range(
        nifty["prev_close"], nifty["high"], nifty["low"]
    )
    b_low, b_high, b_range = get_opening_range(
        banknifty["prev_close"], banknifty["high"], banknifty["low"]
    )

    volatility = get_volatility(n_range)
    behavior = get_behavior(sentiment, nifty_bias)

    msg = "🌅 *PRE-MARKET INDEX INTELLIGENCE*\n\n"

    msg += f"🌍 Global Sentiment: *{sentiment}*\n\n"

    msg += "📊 Index Outlook:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{bank_bias}*\n\n"

    msg += "📍 Expected Opening Zone:\n"
    msg += f"• NIFTY: {n_low} – {n_high}\n"
    msg += f"• BANK NIFTY: {b_low} – {b_high}\n\n"

    msg += f"⚡ Volatility Outlook: *{volatility}*\n\n"

    msg += "📦 Market Behaviour:\n"
    msg += f"• {behavior}\n"
    msg += "• Wait for confirmation after 9:20 AM\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    msg += "\n\n⚠️ Informational only. Not a trading recommendation."

    return msg

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        sentiment = get_global_sentiment()

        nifty = get_index_data("^NSEI")
        banknifty = get_index_data("^NSEBANK")

        if not nifty or not banknifty:
            raise Exception("Index data not available")

        message = create_message(sentiment, nifty, banknifty)

        send_telegram(message)

        print("✅ Market intelligence sent")

    except Exception as e:
        print(f"❌ Error: {e}")
