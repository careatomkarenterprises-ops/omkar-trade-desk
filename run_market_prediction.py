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

            requests.post(url, data=payload, timeout=10)

        except:
            pass

# ============================
# NSE FETCH (PRIMARY DATA)
# ============================
def fetch_nse_index(symbol):
    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        # Required handshake
        session.get("https://www.nseindia.com", headers=headers, timeout=5)

        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        res = session.get(url, headers=headers, timeout=5)
        data = res.json()

        price = data["priceInfo"]["lastPrice"]
        high = data["priceInfo"]["intraDayHighLow"]["max"]
        low = data["priceInfo"]["intraDayHighLow"]["min"]

        return {
            "close": price,
            "high": high,
            "low": low,
            "change": 0  # NSE API doesn't easily give previous % change
        }

    except:
        return None

# ============================
# YAHOO FETCH (GLOBAL OPTIONAL)
# ============================
def safe_fetch(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="1d", progress=False)

        if data is None or data.empty or len(data) < 2:
            return None

        prev = data.iloc[-2]
        curr = data.iloc[-1]

        change = ((curr["Close"] - prev["Close"]) / prev["Close"]) * 100

        return {
            "close": curr["Close"],
            "high": prev["High"],
            "low": prev["Low"],
            "change": change
        }

    except:
        return None

# ============================
# LOGIC
# ============================
def get_bias(change):
    if change > 0.5:
        return "BULLISH"
    elif change < -0.5:
        return "BEARISH"
    return "SIDEWAYS"

def get_range(close, high, low):
    r = high - low
    return round(close - r * 0.25), round(close + r * 0.25), r

def get_volatility(r):
    if r > 350:
        return "HIGH"
    elif r > 180:
        return "NORMAL"
    return "LOW"

def global_score(sp500, nasdaq):
    score = 0
    if sp500 and sp500["change"] > 0:
        score += 1
    if nasdaq and nasdaq["change"] > 0:
        score += 1
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
# MESSAGE
# ============================
def build_message(nifty, banknifty, sp500, nasdaq, vix):

    nifty_bias = "SIDEWAYS"  # NSE doesn’t give % change easily
    bank_bias = "SIDEWAYS"

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

    msg = "🌅 *PRE-MARKET ENGINE (STABLE v2.3)*\n\n"

    msg += f"🌍 Global Score: *{g_score}/2*\n"
    msg += f"📉 VIX: *{vix_state}*\n\n"

    msg += "📊 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}*\n"
    msg += f"• BANK NIFTY: *{bank_bias}*\n\n"

    msg += "📍 Expected Range:\n"
    msg += f"• NIFTY: {n_low} – {n_high}\n"
    msg += f"• BANKNIFTY: {b_low} – {b_high}\n\n"

    msg += f"⚡ Volatility: *{vol}*\n"
    msg += f"🎯 Confidence: *{confidence}*\n\n"

    msg += "📦 Market Behaviour:\n"

    if g_score >= 1:
        msg += "• Momentum influenced by global cues\n"
    else:
        msg += "• Range / Wait for breakout\n"

    msg += "\n⏰ " + datetime.now().strftime('%H:%M:%S')
    msg += "\n\n⚠️ Informational only. Not financial advice."

    return msg

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        print("🚀 Running Stable Pre-Market Engine v2.3")

        # NSE (PRIMARY)
        nifty = fetch_nse_index("NIFTY")
        banknifty = fetch_nse_index("BANKNIFTY")

        # Yahoo (OPTIONAL)
        sp500 = safe_fetch("^GSPC")
        nasdaq = safe_fetch("^IXIC")
        vix = safe_fetch("^VIX")

        if not nifty or not banknifty:
            send_telegram("⚠️ NSE data unavailable. Update after market open.")
        else:
            msg = build_message(nifty, banknifty, sp500, nasdaq, vix)
            send_telegram(msg)

        print("✅ Done")

    except Exception as e:
        print("❌ Fatal Error:", e)
        send_telegram("⚠️ System error. Update after market open.")
