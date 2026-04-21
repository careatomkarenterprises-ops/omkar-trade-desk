import os
import requests
import yfinance as yf
from datetime import datetime

# ============================
# ENV
# ============================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")

# ============================
# TELEGRAM (SAFE LOCAL ENGINE)
# ============================
def send_telegram(message):
    if not BOT_TOKEN or not CHANNEL:
        print("❌ Missing Telegram config")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown"
        }

        r = requests.post(url, data=payload, timeout=10)
        print("✅ Sent" if r.status_code == 200 else r.text)

    except Exception as e:
        print("Telegram error:", e)

# ============================
# MARKET DATA (YFINANCE ONLY)
# ============================
def get_index(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="1d")

        if data is None or len(data) < 2:
            return None

        prev = data.iloc[-2]
        curr = data.iloc[-1]

        change = ((curr["Close"] - prev["Close"]) / prev["Close"]) * 100

        return {
            "prev_close": prev["Close"],
            "high": prev["High"],
            "low": prev["Low"],
            "change": change
        }

    except Exception as e:
        print("YFinance error:", e)
        return None

# ============================
# LOGIC ENGINE (V2 SAFE)
# ============================
def get_bias(change):
    if change > 0.5:
        return "BULLISH"
    elif change < -0.5:
        return "BEARISH"
    return "SIDEWAYS"

def get_range(prev_close, high, low):
    rng = high - low
    return round(prev_close - rng * 0.25), round(prev_close + rng * 0.25), rng

def volatility(rng):
    if rng > 300:
        return "HIGH"
    elif rng > 150:
        return "NORMAL"
    return "LOW"

# ============================
# MESSAGE BUILDER
# ============================
def build_message(nifty, banknifty):
    n_bias = get_bias(nifty["change"])
    b_bias = get_bias(banknifty["change"])

    n_low, n_high, n_rng = get_range(nifty["prev_close"], nifty["high"], nifty["low"])
    b_low, b_high, b_rng = get_range(banknifty["prev_close"], banknifty["high"], banknifty["low"])

    msg = "📊 *INSTITUTIONAL PRE-MARKET ENGINE v2*\n\n"

    msg += f"📍 NIFTY: {n_bias}\n"
    msg += f"📍 BANKNIFTY: {b_bias}\n\n"

    msg += "📌 Expected Range:\n"
    msg += f"NIFTY: {n_low} - {n_high}\n"
    msg += f"BANKNIFTY: {b_low} - {b_high}\n\n"

    msg += f"⚡ NIFTY Volatility: {volatility(n_rng)}\n"
    msg += f"⚡ BANKNIFTY Volatility: {volatility(b_rng)}\n\n"

    msg += "🧠 Note: Derived from price structure + momentum model\n"
    msg += "⚠️ Educational use only\n"
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("🚀 Running Pre-Market Engine v2")

    nifty = get_index("^NSEI")
    banknifty = get_index("^NSEBANK")

    if not nifty or not banknifty:
        send_telegram("⚠️ Data unavailable for pre-market engine")
    else:
        message = build_message(nifty, banknifty)
        print(message)
        send_telegram(message)

    print("✅ Done")
