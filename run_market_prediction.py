import os
import requests
import yfinance as yf
import time
from datetime import datetime

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
        print("❌ TELEGRAM TOKEN MISSING")
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
# SAFE FETCH (RETRY SYSTEM)
# ============================
def safe_fetch(symbol, retries=3):
    for attempt in range(retries):
        try:
            data = yf.download(symbol, period="5d", interval="1d", progress=False)

            if data is not None and not data.empty:
                return data

        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed for {symbol}: {e}")

        time.sleep(1)

    print(f"❌ Failed to fetch {symbol}")
    return None

# ============================
# SYMBOLS + FALLBACKS
# ============================
SYMBOLS = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
    "VIX": "^INDIAVIX"
}

FALLBACKS = {
    "^GSPC": "SPY",
    "^IXIC": "QQQ",
    "^INDIAVIX": "^VIX"
}

def get_data(symbol):
    data = safe_fetch(symbol)

    if data is None and symbol in FALLBACKS:
        print(f"🔁 Using fallback for {symbol}")
        data = safe_fetch(FALLBACKS[symbol])

    return data

# ============================
# DATA PROCESSING
# ============================
def extract_metrics(data):
    if data is None or len(data) < 2:
        return None

    prev = data.iloc[-2]
    curr = data.iloc[-1]

    change = ((curr["Close"] - prev["Close"]) / prev["Close"]) * 100
    high = prev["High"]
    low = prev["Low"]
    close = prev["Close"]

    return {
        "change": change,
        "high": high,
        "low": low,
        "close": close
    }

# ============================
# LOGIC ENGINE
# ============================
def get_bias(change):
    if change > 0.5:
        return "BULLISH"
    elif change < -0.5:
        return "BEARISH"
    return "SIDEWAYS"

def get_range(close, high, low):
    r = high - low
    return round(close - r*0.25), round(close + r*0.25), r

def get_volatility(r):
    if r > 350:
        return "HIGH"
    elif r > 180:
        return "NORMAL"
    return "LOW"

def global_score(sp500, nasdaq):
    score = 0
    if sp500 and sp500["change"] > 0: score += 1
    if nasdaq and nasdaq["change"] > 0: score += 1
    return score

def vix_sentiment(vix):
    if not vix:
        return "UNKNOWN"
    if vix["close"] > 18:
        return "HIGH RISK"
    elif vix["close"] < 13:
        return "LOW RISK"
    return "NORMAL"

# ============================
# MESSAGE BUILDER
# ============================
def build_message(nifty, banknifty, sp500, nasdaq, vix):

    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(banknifty["change"])

    n_low, n_high, n_range = get_range(nifty["close"], nifty["high"], nifty["low"])
    b_low, b_high, b_range = get_range(banknifty["close"], banknifty["high"], banknifty["low"])

    vol = get_volatility(n_range)
    g_score = global_score(sp500, nasdaq)
    vix_state = vix_sentiment(vix)

    confidence = "LOW"
    if g_score == 2:
        confidence = "HIGH"
    elif g_score == 1:
        confidence = "MEDIUM"

    msg = "🌅 *INSTITUTIONAL PRE-MARKET ENGINE v2.2*\n\n"

    msg += f"🌍 Global Score: *{g_score}/2*\n"
    msg += f"📉 VIX Sentiment: *{vix_state}*\n\n"

    msg += "📊 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{bank_bias}*\n\n"

    msg += "📍 Expected Range:\n"
    msg += f"• NIFTY: {n_low} – {n_high}\n"
    msg += f"• BANKNIFTY: {b_low} – {b_high}\n\n"

    msg += f"⚡ Volatility: *{vol}*\n"
    msg += f"🎯 Confidence: *{confidence}*\n\n"

    msg += "📦 Market Behaviour:\n"

    if nifty_bias == "BULLISH" and g_score >= 1:
        msg += "• Trend Up / Buy on Dips\n"
    elif nifty_bias == "BEARISH" and g_score == 0:
        msg += "• Trend Down / Sell on Rise\n"
    else:
        msg += "• Range / Wait for Breakout\n"

    msg += "\n⏰ " + datetime.now().strftime('%H:%M:%S')
    msg += "\n\n⚠️ Informational only. Not financial advice."

    return msg

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        print("🚀 Running Institutional Engine v2.2")

        nifty = extract_metrics(get_data(SYMBOLS["NIFTY"]))
        banknifty = extract_metrics(get_data(SYMBOLS["BANKNIFTY"]))
        sp500 = extract_metrics(get_data(SYMBOLS["SP500"]))
        nasdaq = extract_metrics(get_data(SYMBOLS["NASDAQ"]))
        vix = extract_metrics(get_data(SYMBOLS["VIX"]))

        if not nifty or not banknifty:
            print("❌ Critical data missing")
            send_telegram("⚠️ Pre-market data unavailable. Update after open.")
        else:
            msg = build_message(nifty, banknifty, sp500, nasdaq, vix)
            print(msg)
            send_telegram(msg)

        print("✅ Done")

    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        send_telegram("⚠️ System error. Update after market open.")
