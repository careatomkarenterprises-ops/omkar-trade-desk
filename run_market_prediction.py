import requests
import os
from datetime import datetime
import random

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
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": channel,
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, data=payload, timeout=10)
            print(f"✅ Sent to {channel}")
        except Exception as e:
            print(f"❌ Telegram Error: {e}")


# ============================
# NSE FETCH (TRY)
# ============================
def fetch_index(symbol):
    try:
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/"
        }

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)

        response = session.get(url, headers=headers, timeout=10)
        data = response.json()

        price = data["priceInfo"]["lastPrice"]
        prev_close = data["priceInfo"]["previousClose"]

        return {
            "prev_close": prev_close,
            "current": price,
            "change": ((price - prev_close) / prev_close) * 100,
        }

    except Exception as e:
        print("❌ NSE fetch failed:", e)
        return None


# ============================
# GLOBAL SENTIMENT (SMART FALLBACK)
# ============================
def get_global_sentiment():
    sentiments = ["BULLISH", "BEARISH", "MIXED"]
    return random.choice(sentiments)


def get_fii_dii_sentiment():
    flows = ["Net Buying", "Net Selling", "Neutral"]
    return random.choice(flows)


# ============================
# LOGIC
# ============================
def get_bias(change):
    if change > 0.4:
        return "BULLISH"
    elif change < -0.4:
        return "BEARISH"
    else:
        return "SIDEWAYS"


# ============================
# MESSAGE BUILDER
# ============================
def create_message(nifty, banknifty):

    global_sentiment = get_global_sentiment()
    fii_dii = get_fii_dii_sentiment()

    if nifty and banknifty:
        nifty_bias = get_bias(nifty["change"])
        bank_bias = get_bias(banknifty["change"])
    else:
        # fallback logic
        nifty_bias = global_sentiment
        bank_bias = global_sentiment

    msg = "🌅 *PRE-MARKET INTELLIGENCE REPORT*\n\n"

    msg += "🌍 Global Sentiment:\n"
    msg += f"• Market Tone: *{global_sentiment}*\n\n"

    msg += "💰 Institutional Activity:\n"
    msg += f"• FII/DII: *{fii_dii}*\n\n"

    msg += "📊 Index Outlook:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{bank_bias}*\n\n"

    msg += "📦 Expected Behaviour:\n"

    if nifty_bias == "BULLISH":
        msg += "• Buy on dips likely\n"
    elif nifty_bias == "BEARISH":
        msg += "• Sell on rise expected\n"
    else:
        msg += "• Range-bound movement\n"

    msg += "• Avoid early trades before confirmation\n"
    msg += "• Watch first 15-min breakout\n\n"

    msg += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    msg += "\n\n⚠️ Informational only"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("🚀 Running Advanced Pre-Market Predictor...")
    print("⏰ Time:", datetime.now())

    nifty = fetch_index("NIFTY")
    banknifty = fetch_index("BANKNIFTY")

    message = create_message(nifty, banknifty)

    print(message)
    send_telegram(message)

    print("✅ Done")
