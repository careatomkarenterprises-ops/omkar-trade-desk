import requests
import os
import time
from datetime import datetime
import yfinance as yf

# ============================
# ENV VARIABLES
# ============================
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
# SAFE DATA FETCH (FIXED)
# ============================
def safe_fetch(symbol, retries=3):
    for attempt in range(retries):
        try:
            data = yf.download(
                symbol,
                period="5d",
                interval="1d",
                progress=False,
                threads=False
            )

            if data is not None and not data.empty:
                prev = data.iloc[-2]
                current = data.iloc[-1]

                return {
                    "prev_close": float(prev["Close"]),
                    "close": float(current["Close"]),
                    "high": float(prev["High"]),
                    "low": float(prev["Low"]),
                    "change": ((current["Close"] - prev["Close"]) / prev["Close"]) * 100
                }

        except Exception as e:
            print(f"Retry {attempt+1} failed for {symbol}: {e}")
            time.sleep(2)

    print(f"❌ Final failure for {symbol}")
    return None

# ============================
# DATA FETCH WITH FALLBACK
# ============================
def get_market_data():
    nifty = safe_fetch("^NSEI")
    banknifty = safe_fetch("^NSEBANK")

    # Fallback ETFs (VERY IMPORTANT)
    if not nifty:
        print("🔁 Using NIFTY ETF fallback")
        nifty = safe_fetch("NIFTYBEES.NS")

    if not banknifty:
        print("🔁 Using BANK ETF fallback")
        banknifty = safe_fetch("BANKBEES.NS")

    return nifty, banknifty

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

    msg = "🌅 *PRE-MARKET INDEX INTELLIGENCE (v2.2)*\n\n"

    msg += "📊 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{bank_bias}*\n\n"

    msg += "📍 Expected Opening Zone:\n"
    msg += f"• NIFTY: {n_low} – {n_high}\n"
    msg += f"• BANK NIFTY: {b_low} – {b_high}\n\n"

    msg += f"⚡ Volatility: *{volatility}*\n\n"

    msg += "📦 Market Behaviour:\n"
    msg += "• Wait for confirmation after 9:20 AM\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    msg += "\n\n⚠️ Informational only. Not financial advice."

    return msg

# ============================
# FALLBACK MESSAGE
# ============================
def fallback_message():
    return (
        "⚠️ *Pre-Market Update*\n\n"
        "Market data temporarily unavailable.\n"
        "Update will be shared after open.\n\n"
        "⏰ " + datetime.now().strftime('%H:%M:%S')
    )

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        print("🚀 Running Pre-Market Engine v2.2")

        nifty, banknifty = get_market_data()

        if not nifty or not banknifty:
            print("❌ Critical data missing")
            send_telegram(fallback_message())
        else:
            message = create_message(nifty, banknifty)
            print(message)
            send_telegram(message)

        print("✅ Done")

    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        send_telegram(fallback_message())
