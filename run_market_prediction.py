import requests
import os
import time
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
# TELEGRAM (DEBUG ENABLED)
# ============================
def send_telegram(message):
    if not BOT_TOKEN:
        print("❌ Missing TELEGRAM_BOT_TOKEN")
        return

    for channel in CHANNELS:
        if not channel:
            print("⚠️ Skipping empty channel")
            continue

        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": channel,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = requests.post(url, data=payload, timeout=10)

            if response.status_code == 200:
                print(f"✅ Sent to {channel}")
            else:
                print(f"❌ Failed for {channel}: {response.text}")

        except Exception as e:
            print(f"❌ Error sending to {channel}: {e}")


# ============================
# GLOBAL SENTIMENT (SAFE MODE)
# ============================
def get_global_sentiment():
    try:
        tickers = ["^DJI", "^IXIC", "^GSPC"]
        score = 0
        success = 0

        for t in tickers:
            try:
                df = yf.Ticker(t).history(period="1d")
                if df is not None and not df.empty:
                    success += 1
                    if df["Close"].iloc[-1] > df["Open"].iloc[-1]:
                        score += 1
            except:
                continue

        if success == 0:
            return "NEUTRAL", 0

        if score == 3:
            return "STRONG BULLISH", score
        elif score == 2:
            return "BULLISH", score
        elif score == 1:
            return "MIXED", score
        else:
            return "BEARISH", score

    except Exception as e:
        print("❌ Sentiment Error:", e)
        return "NEUTRAL", 0


# ============================
# INDEX DATA (WITH RETRY)
# ============================
def get_index_data(symbol):
    for attempt in range(3):
        try:
            df = yf.Ticker(symbol).history(period="2d")

            if df is not None and not df.empty and len(df) >= 2:
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

        except Exception as e:
            print(f"⚠️ Retry {attempt+1} failed for {symbol}: {e}")

        time.sleep(2)

    print(f"❌ Not enough data for {symbol}")
    return None


# ============================
# BIAS
# ============================
def get_bias(change):
    if change > 0.4:
        return "BULLISH"
    elif change < -0.4:
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
    if range_size > 350:
        return "HIGH"
    elif range_size > 180:
        return "NORMAL"
    else:
        return "LOW"


# ============================
# CONFIDENCE
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
# MESSAGE
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
    msg += "\n\n⚠️ Informational only. Not a trading recommendation."

    return msg


# ============================
# MAIN (FAIL-SAFE)
# ============================
if __name__ == "__main__":
    try:
        print("🚀 Running Market Predictor...")

        sentiment, score = get_global_sentiment()

        nifty = get_index_data("^NSEI")
        banknifty = get_index_data("^NSEBANK")

        # ✅ FAIL SAFE MESSAGE
        if not nifty or not banknifty:
            fallback_msg = "⚠️ Market data temporarily unavailable.\n\nPlease wait for next update."
            send_telegram(fallback_msg)
            print("❌ Data missing - fallback message sent")
            exit()

        message = create_message(sentiment, score, nifty, banknifty)

        print("📩 Message Generated:")
        print(message)

        send_telegram(message)

        print("✅ Done")

    except Exception as e:
        print(f"❌ Error: {e}")
