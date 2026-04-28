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
# TELEGRAM (WITH STATUS CHECK)
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
# NSE FETCH (STABLE VERSION)
# ============================
def fetch_nse_index(symbol):
    url = "https://www.nseindia.com/api/chart-databyindex"
    params = {"index": symbol}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive"
    }

    session = requests.Session()

    for attempt in range(3):
        try:
            # Step 1: Load homepage (important for cookies)
            session.get("https://www.nseindia.com", headers=headers, timeout=5)

            # Step 2: Fetch data
            response = session.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                print(f"❌ NSE HTTP Error: {response.status_code}")
                time.sleep(2)
                continue

            data = response.json()

            values = data.get("grapthData", [])

            if len(values) < 2:
                print("❌ Not enough data points")
                return None

            prev = values[-2][1]
            current = values[-1][1]

            return {
                "prev_close": prev,
                "current": current,
                "change": ((current - prev) / prev) * 100,
                "high": prev * 1.01,
                "low": prev * 0.99
            }

        except Exception as e:
            print(f"🔁 Retry {attempt+1} NSE failed:", e)
            time.sleep(3)

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
# FALLBACK MESSAGE
# ============================
def fallback_message():
    msg = "🌅 *PRE-MARKET UPDATE*\n\n"
    msg += "⚠️ Data temporarily unavailable\n\n"
    msg += "📌 Trade Plan:\n"
    msg += "• Wait for first 15 minutes\n"
    msg += "• Avoid early volatility\n"
    msg += "• Trade with confirmation only\n\n"
    msg += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("🚀 Running Production Pre-Market Predictor...")
    print("⏰ Time:", datetime.now())

    nifty = fetch_nse_index("NIFTY 50")
    banknifty = fetch_nse_index("NIFTY BANK")

    if not nifty or not banknifty:
        print("❌ Data fetch failed → sending fallback")
        send_telegram(fallback_message())
    else:
        message = create_message(nifty, banknifty)
        print(message)
        send_telegram(message)

    print("✅ Done")
