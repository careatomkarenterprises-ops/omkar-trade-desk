import requests
import os
import time
from datetime import datetime

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
# NSE QUOTE API (MORE STABLE)
# ============================
def fetch_index(symbol):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()

    try:
        # Step 1: Get cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=5)

        # Step 2: Fetch data
        response = session.get(url, headers=headers, timeout=10)
        data = response.json()

        price = data["priceInfo"]["lastPrice"]
        prev_close = data["priceInfo"]["previousClose"]

        return {
            "prev_close": prev_close,
            "current": price,
            "change": ((price - prev_close) / prev_close) * 100,
            "high": data["priceInfo"]["intraDayHighLow"]["max"],
            "low": data["priceInfo"]["intraDayHighLow"]["min"]
        }

    except Exception as e:
        print("❌ NSE fetch failed:", e)
        return None


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


def get_opening_range(prev_close, high, low):
    range_size = high - low
    low_range = prev_close - (range_size * 0.25)
    high_range = prev_close + (range_size * 0.25)
    return round(low_range), round(high_range), range_size


def get_volatility(range_size):
    if range_size > 300:
        return "HIGH"
    elif range_size > 150:
        return "NORMAL"
    else:
        return "LOW"


# ============================
# MESSAGE
# ============================
def create_message(nifty, banknifty):

    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(banknifty["change"])

    n_low, n_high, n_range = get_opening_range(
        nifty["prev_close"], nifty["high"], nifty["low"]
    )

    b_low, b_high, b_range = get_opening_range(
        banknifty["prev_close"], banknifty["high"], banknifty["low"]
    )

    volatility = get_volatility(n_range)

    msg = "🌅 *PRE-MARKET INTELLIGENCE*\n\n"

    msg += "📊 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{bank_bias}*\n\n"

    msg += "📍 Opening Zone:\n"
    msg += f"• NIFTY: {n_low} – {n_high}\n"
    msg += f"• BANK NIFTY: {b_low} – {b_high}\n\n"

    msg += f"⚡ Volatility: *{volatility}*\n\n"

    msg += "📦 Market Behaviour:\n"
    if nifty_bias == "BULLISH":
        msg += "• Trend Up Day\n"
    elif nifty_bias == "BEARISH":
        msg += "• Trend Down Day\n"
    else:
        msg += "• Range-bound\n"

    msg += "• Wait for 9:20 confirmation\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    msg += "\n\n⚠️ Informational only."

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("🚀 Running Production Pre-Market Predictor...")
    print("⏰ Time:", datetime.now())

    # IMPORTANT: Use correct symbols
    nifty = fetch_index("NIFTY")
    banknifty = fetch_index("BANKNIFTY")

    if not nifty or not banknifty:
        print("❌ Data fetch failed → sending fallback")

        fallback = f"""
🌅 *PRE-MARKET UPDATE*

📊 Market preparing for open  
📍 Awaiting confirmation from opening price  

⏰ {datetime.now().strftime('%H:%M:%S')}

⚠️ Informational only
"""
        send_telegram(fallback)

    else:
        message = create_message(nifty, banknifty)
        print(message)
        send_telegram(message)

    print("✅ Done")
