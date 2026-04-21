import os
import requests
import yfinance as yf
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")

# ============================
# TELEGRAM SAFE
# ============================
def send(msg):
    if not BOT_TOKEN or not CHANNEL:
        print("Missing config")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHANNEL,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# ============================
# SAFE YFINANCE WRAPPER
# ============================
def safe_fetch(symbol):
    for _ in range(2):  # retry twice
        try:
            df = yf.download(symbol, period="5d", interval="1d", progress=False)

            if df is not None and len(df) >= 2:
                prev = df.iloc[-2]
                curr = df.iloc[-1]

                change = ((curr["Close"] - prev["Close"]) / prev["Close"]) * 100

                return {
                    "prev_close": prev["Close"],
                    "high": prev["High"],
                    "low": prev["Low"],
                    "change": change
                }

        except Exception as e:
            print(f"Retry fetch {symbol}: {e}")

    # fallback (IMPORTANT)
    return {
        "prev_close": 0,
        "high": 0,
        "low": 0,
        "change": 0
    }

# ============================
# MARKET STATE ENGINE
# ============================
def bias(c):
    if c > 0.5:
        return "BULLISH"
    if c < -0.5:
        return "BEARISH"
    return "SIDEWAYS"

def rng(p, h, l):
    r = max(h - l, 1)
    return round(p - r * 0.3), round(p + r * 0.3), r

def volatility(r):
    if r > 300:
        return "HIGH"
    if r > 150:
        return "NORMAL"
    return "LOW"

# ============================
# MESSAGE
# ============================
def build(n, b, gsent):
    nb = bias(n["change"])
    bb = bias(b["change"])

    nl, nh, nr = rng(n["prev_close"], n["high"], n["low"])
    bl, bh, br = rng(b["prev_close"], b["high"], b["low"])

    msg = "📊 *INSTITUTIONAL PRE-MARKET ENGINE v2.2*\n\n"

    msg += f"🌍 Global: {gsent}\n\n"

    msg += f"NIFTY: {nb}\nBANKNIFTY: {bb}\n\n"

    msg += "📍 RANGE\n"
    msg += f"NIFTY: {nl} - {nh}\n"
    msg += f"BANKNIFTY: {bl} - {bh}\n\n"

    msg += "⚡ VOLATILITY\n"
    msg += f"NIFTY: {volatility(nr)}\nBANKNIFTY: {volatility(br)}\n\n"

    if nb == bb:
        msg += "🔥 UNIFIED MARKET DIRECTION\n"
    else:
        msg += "⚠️ MIXED STRUCTURE\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    msg += "\n⚠️ Educational only"

    return msg

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("🚀 Engine v2.2 starting")

    nifty = safe_fetch("^NSEI")
    bank = safe_fetch("^NSEBANK")

    # global safe fallback
    gsent = "NEUTRAL (CI MODE)"

    msg = build(nifty, bank, gsent)

    print(msg)
    send(msg)

    print("✅ Done")
