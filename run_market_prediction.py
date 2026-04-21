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
# TELEGRAM
# ============================
def send_telegram(msg):
    if not BOT_TOKEN or not CHANNEL:
        print("Missing Telegram config")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHANNEL,
            "text": msg,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print("Telegram error:", e)

# ============================
# MARKET DATA
# ============================
def get_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1d")
        if df is None or len(df) < 2:
            return None

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        change = ((curr["Close"] - prev["Close"]) / prev["Close"]) * 100

        return {
            "prev_close": prev["Close"],
            "high": prev["High"],
            "low": prev["Low"],
            "close": curr["Close"],
            "change": change
        }

    except Exception as e:
        print("YF error:", e)
        return None

# ============================
# GLOBAL SENTIMENT
# ============================
def global_sentiment():
    us = yf.download("^GSPC", period="5d", interval="1d")
    if us is None or len(us) < 2:
        return "NEUTRAL", 50

    change = ((us["Close"].iloc[-1] - us["Close"].iloc[-2]) / us["Close"].iloc[-2]) * 100

    if change > 0.5:
        return "RISK-ON", 70
    elif change < -0.5:
        return "RISK-OFF", 30
    return "NEUTRAL", 50

# ============================
# ENGINE LOGIC
# ============================
def bias(change):
    if change > 0.6:
        return "BULLISH"
    elif change < -0.6:
        return "BEARISH"
    return "SIDEWAYS"

def trend_score(change):
    return min(100, int(abs(change) * 20))

def volatility(r):
    if r > 400:
        return "HIGH"
    elif r > 200:
        return "NORMAL"
    return "LOW"

def range_calc(prev, high, low):
    rng = high - low
    return round(prev - rng * 0.3), round(prev + rng * 0.3), rng

# ============================
# MESSAGE
# ============================
def build(nifty, bank, gsent, gscore):

    n_bias = bias(nifty["change"])
    b_bias = bias(bank["change"])

    n_score = trend_score(nifty["change"])
    b_score = trend_score(bank["change"])

    n_low, n_high, n_rng = range_calc(nifty["prev_close"], nifty["high"], nifty["low"])
    b_low, b_high, b_rng = range_calc(bank["prev_close"], bank["high"], bank["low"])

    msg = "📊 *INSTITUTIONAL PRE-MARKET ENGINE v2.1*\n\n"

    msg += f"🌍 Global: {gsent} ({gscore})\n\n"

    msg += "📌 INDEX STRUCTURE\n"
    msg += f"NIFTY: {n_bias} | Score: {n_score}/100\n"
    msg += f"BANKNIFTY: {b_bias} | Score: {b_score}/100\n\n"

    msg += "📍 EXPECTED RANGE\n"
    msg += f"NIFTY: {n_low} - {n_high}\n"
    msg += f"BANKNIFTY: {b_low} - {b_high}\n\n"

    msg += "⚡ VOLATILITY\n"
    msg += f"NIFTY: {volatility(n_rng)}\n"
    msg += f"BANKNIFTY: {volatility(b_rng)}\n\n"

    # SMART FLOW INTERPRETATION
    if n_score > 70 and b_score > 70:
        msg += "🔥 STRONG TREND DAY EXPECTED\n"
    elif n_score < 40 and b_score < 40:
        msg += "⚠️ CHOPPY / RANGE MARKET\n"
    else:
        msg += "📉 MIXED / SELECTIVE MOVES EXPECTED\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    msg += "\n⚠️ Educational analysis only"

    return msg

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("🚀 Running Institutional Engine v2.1")

    nifty = get_data("^NSEI")
    bank = get_data("^NSEBANK")
    gsent, gscore = global_sentiment()

    if not nifty or not bank:
        send_telegram("⚠️ Market data unavailable")
    else:
        msg = build(nifty, bank, gsent, gscore)
        print(msg)
        send_telegram(msg)

    print("✅ Done")
