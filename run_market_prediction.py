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
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": channel, "text": message, "parse_mode": "Markdown"},
                timeout=10
            )
        except Exception as e:
            print("Telegram Error:", e)

# ============================
# NSE FETCH
# ============================
def get_nse_index(symbol):
    try:
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={symbol}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/"
        }

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        res = session.get(url, headers=headers, timeout=10)

        data = res.json()["data"][0]

        return {
            "price": data["lastPrice"],
            "change": data["pChange"]
        }

    except Exception as e:
        print("NSE Error:", e)
        return None

# ============================
# YFINANCE BACKUP
# ============================
def get_yf(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1d")

        if df.empty:
            return None

        prev = df["Close"].iloc[-2]
        curr = df["Close"].iloc[-1]

        change = ((curr - prev) / prev) * 100

        return {"price": curr, "change": change}

    except:
        return None

# ============================
# SMART FETCH
# ============================
def get_index(nse, yf_symbol):
    data = get_nse_index(nse)
    if data:
        return data

    print(f"⚠️ Falling back to YF: {yf_symbol}")
    return get_yf(yf_symbol)

# ============================
# GLOBAL SENTIMENT
# ============================
def global_sentiment():
    sp = get_yf("^GSPC")
    nq = get_yf("^IXIC")

    score = 0

    if sp and sp["change"] > 0:
        score += 1
    else:
        score -= 1

    if nq and nq["change"] > 0:
        score += 1
    else:
        score -= 1

    if score > 0:
        return "BULLISH", score
    elif score < 0:
        return "BEARISH", score
    return "NEUTRAL", score

# ============================
# INDIA VIX
# ============================
def get_vix():
    vix = get_yf("^INDIAVIX")
    if not vix:
        return 15  # safe fallback

    return vix["price"]

# ============================
# BIAS
# ============================
def get_bias(change):
    if change > 0.5:
        return "BULLISH"
    elif change < -0.5:
        return "BEARISH"
    return "SIDEWAYS"

# ============================
# PCR PROXY (SIMULATED)
# ============================
def pcr_proxy(nifty_change, vix):

    if nifty_change > 0 and vix < 15:
        return "LOW PCR (Bullish)"
    elif nifty_change < 0 and vix > 15:
        return "HIGH PCR (Bearish)"
    return "BALANCED"

# ============================
# CONFIDENCE SCORE
# ============================
def confidence_score(sentiment_score, nifty_bias, vix):

    score = 50

    score += sentiment_score * 10

    if nifty_bias == "BULLISH":
        score += 10
    elif nifty_bias == "BEARISH":
        score += 10

    if vix < 14:
        score += 10
    elif vix > 18:
        score -= 10

    return max(0, min(100, score))

# ============================
# MARKET STRUCTURE
# ============================
def market_structure(nifty_bias, bank_bias, vix):

    if nifty_bias == bank_bias and vix < 15:
        return "TREND DAY"
    elif vix > 18:
        return "HIGH VOLATILE / TRAP"
    return "RANGE / STOCK SPECIFIC"

# ============================
# MESSAGE
# ============================
def build_message(sentiment, score, nifty, bank, vix):

    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(bank["change"])

    pcr = pcr_proxy(nifty["change"], vix)

    confidence = confidence_score(score, nifty_bias, vix)

    structure = market_structure(nifty_bias, bank_bias, vix)

    msg = "🔥 *INSTITUTIONAL PRE-MARKET ENGINE v2.2*\n\n"

    msg += f"🌍 Global Sentiment: *{sentiment}*\n"
    msg += f"📊 Confidence Score: *{confidence}/100*\n\n"

    msg += "📈 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}* ({nifty['change']:.2f}%)\n"
    msg += f"• BANKNIFTY: *{bank_bias}* ({bank['change']:.2f}%)\n\n"

    msg += "🧠 Options Intelligence:\n"
    msg += f"• PCR Sentiment: *{pcr}*\n"
    msg += f"• India VIX: *{vix:.2f}*\n\n"

    msg += "📦 Market Structure:\n"
    msg += f"• {structure}\n"
    msg += "• Wait for 9:20 confirmation\n\n"

    msg += "⚠️ Informational only. No investment advice."
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:

        print("🚀 Running Institutional Engine v2.2")

        sentiment, score = global_sentiment()

        nifty = get_index("NIFTY 50", "^NSEI")
        bank = get_index("NIFTY BANK", "^NSEBANK")

        vix = get_vix()

        if not nifty or not bank:
            send_telegram("⚠️ Market data unavailable")
        else:
            msg = build_message(sentiment, score, nifty, bank, vix)
            send_telegram(msg)

        print("✅ Done")

    except Exception as e:
        print("❌ Error:", e)
