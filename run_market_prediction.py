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
# TELEGRAM (MULTI CHANNEL SAFE)
# ============================
def send_telegram(message):
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
            requests.post(url, data=payload, timeout=10)
        except:
            continue


# ============================
# GLOBAL SENTIMENT (STRONGER)
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

        if score == 3:
            return "STRONG BULLISH", score
        elif score == 2:
            return "BULLISH", score
        elif score == 1:
            return "MIXED", score
        else:
            return "BEARISH", score

    except:
        return "NEUTRAL", 0


# ============================
# INDEX DATA
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
# BIAS LOGIC
# ============================
def get_bias(change):
    if change > 0.4:
        return "BULLISH"
    elif change < -0.4:
        return "BEARISH"
    else:
        return "SIDEWAYS"


# ============================
# OPENING RANGE MODEL
# ============================
def get_opening_range(prev_close, high, low):
    range_size = high - low

    low_range = prev_close - (range_size * 0.25)
    high_range = prev_close + (range_size * 0.25)

    return round(low_range), round(high_range), range_size


# ============================
# VOLATILITY MODEL
# ============================
def get_volatility(range_size):
    if range_size > 350:
        return "HIGH"
    elif range_size > 180:
        return "NORMAL"
    else:
        return "LOW"


# ============================
# CONFIDENCE ENGINE (NEW)
# ============================
def get_confidence(sentiment_score, nifty_bias):
    if sentiment_score >= 2 and nifty_bias == "BULLISH":
        return "HIGH"
    elif sentiment_score == 0 and nifty_bias == "BEARISH":
        return "HIGH"
    elif sentiment_score == 1:
        return "MEDIUM"
    else:
        return "LOW"


# ============================
# MARKET BEHAVIOR
# ============================
def get_behavior(sentiment, bias):
    if "BULLISH" in sentiment and bias == "BULLISH":
        return "Trend Up Day"
    elif "BEARISH" in sentiment and bias == "BEARISH":
        return "Trend Down Day"
    elif bias == "SIDEWAYS":
        return "Range-bound"
    else:
        return "Volatile / Uncertain"


# ============================
# MESSAGE ENGINE (CLEAN + STRONG)
# ============================
def create_message(sentiment, sentiment_score, nifty, banknifty):
    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(banknifty["change"])

    n_low, n_high, n_range = get_opening_range(
        nifty["prev_close"], nifty["high"], nifty["low"]
    )
    b_low, b_high, b_range = get_opening_range(
        banknifty["prev_close"], banknifty["high"], banknifty["low"]
    )

    volatility = get_volatility(n_range)
    confidence = get_confidence(sentiment_score, nifty_bias)
    behavior = get_behavior(sentiment, nifty_bias)

    msg = "🌅 *PRE-MARKET INDEX INTELLIGENCE (LEVEL 3)*\n\n"

    # GLOBAL
    msg += f"🌍 Global Sentiment: *{sentiment}*\n"

    # INDEX
    msg += "\n📊 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{bank_bias}*\n"

    # RANGE
    msg += "\n📍 Expected Opening Zone:\n"
    msg += f"• NIFTY: {n_low} – {n_high}\n"
    msg += f"• BANK NIFTY: {b_low} – {b_high}\n"

    # VOLATILITY
    msg += f"\n⚡ Volatility: *{volatility}*\n"

    # CONFIDENCE
    msg += f"\n🎯 Confidence Level: *{confidence}*\n"

    # BEHAVIOR
    msg += "\n📦 Market Behaviour:\n"
    msg += f"• {behavior}\n"
    msg += "• Wait for price confirmation after 9:20 AM\n"

    # TIME
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    # DISCLAIMER
    msg += "\n\n⚠️ Data-driven market view for educational purposes only."

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        sentiment, score = get_global_sentiment()

        nifty = get_index_data("^NSEI")
        banknifty = get_index_data("^NSEBANK")

        if not nifty or not banknifty:
            raise Exception("Index data not available")

        message = create_message(sentiment, score, nifty, banknifty)

        send_telegram(message)

        print("✅ Level 3 Market Intelligence Sent")

    except Exception as e:
        print(f"❌ Error: {e}")
