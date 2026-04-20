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
# NIFTY BIAS
# ============================
def get_nifty_bias():
    try:
        nifty = yf.Ticker("^NSEI").history(period="2d")

        if len(nifty) < 2:
            return "SIDEWAYS"

        prev_close = nifty["Close"].iloc[-2]
        current = nifty["Close"].iloc[-1]

        change = ((current - prev_close) / prev_close) * 100

        if change > 0.3:
            return "BULLISH"
        elif change < -0.3:
            return "BEARISH"
        else:
            return "SIDEWAYS"

    except:
        return "UNKNOWN"

# ============================
# BANKNIFTY BIAS
# ============================
def get_banknifty_bias():
    try:
        banknifty = yf.Ticker("^NSEBANK").history(period="2d")

        if len(banknifty) < 2:
            return "SIDEWAYS"

        prev_close = banknifty["Close"].iloc[-2]
        current = banknifty["Close"].iloc[-1]

        change = ((current - prev_close) / prev_close) * 100

        if change > 0.3:
            return "BULLISH"
        elif change < -0.3:
            return "BEARISH"
        else:
            return "SIDEWAYS"

    except:
        return "UNKNOWN"

# ============================
# MESSAGE
# ============================
def create_message(sentiment, nifty_bias, banknifty_bias):
    msg = "🌅 *PRE-MARKET INDEX INTELLIGENCE*\n\n"

    msg += f"🌍 Global Sentiment: *{sentiment}*\n\n"

    msg += "📊 Index Outlook:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{banknifty_bias}*\n\n"

    msg += "📦 Insight:\n"
    msg += "• Based on global cues & index behavior\n"
    msg += "• Use with price action confirmation after open\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    msg += "\n\n⚠️ Informational only. Not a trading recommendation."

    return msg

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        sentiment = get_global_sentiment()
        nifty_bias = get_nifty_bias()
        banknifty_bias = get_banknifty_bias()

        message = create_message(sentiment, nifty_bias, banknifty_bias)

        send_telegram(message)

        print("✅ Market prediction sent")

    except Exception as e:
        print(f"❌ Error: {e}")
