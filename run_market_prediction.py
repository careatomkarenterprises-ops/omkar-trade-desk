import requests
import os
from datetime import datetime, timedelta
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
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={
                "chat_id": channel,
                "text": message,
                "parse_mode": "Markdown"
            }, timeout=10)
        except Exception as e:
            print("Telegram Error:", e)


# ============================
# NSE DATA (PRIMARY SOURCE)
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

        data = res.json()

        index = data["data"][0]

        return {
            "price": index["lastPrice"],
            "change": index["pChange"]
        }

    except Exception as e:
        print("NSE Error:", e)
        return None


# ============================
# YFINANCE BACKUP
# ============================
def get_yf_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1d")

        if df.empty:
            return None

        prev_close = df["Close"].iloc[-2]
        current = df["Close"].iloc[-1]

        change = ((current - prev_close) / prev_close) * 100

        return {
            "price": current,
            "change": change
        }

    except Exception as e:
        print("YF Error:", e)
        return None


# ============================
# GET INDEX (SMART FETCH)
# ============================
def get_index_data(nse_symbol, yf_symbol):

    data = get_nse_index(nse_symbol)

    if data:
        return data

    print("⚠️ Falling back to yfinance...")

    return get_yf_data(yf_symbol)


# ============================
# GLOBAL SENTIMENT
# ============================
def get_global_sentiment():

    try:
        sp500 = get_yf_data("^GSPC")
        nasdaq = get_yf_data("^IXIC")

        score = 0

        if sp500 and sp500["change"] > 0:
            score += 1
        else:
            score -= 1

        if nasdaq and nasdaq["change"] > 0:
            score += 1
        else:
            score -= 1

        if score > 0:
            return "BULLISH", score
        elif score < 0:
            return "BEARISH", score
        return "NEUTRAL", score

    except:
        return "NEUTRAL", 0


# ============================
# LOGIC
# ============================
def get_bias(change):
    if change > 0.4:
        return "BULLISH"
    elif change < -0.4:
        return "BEARISH"
    return "SIDEWAYS"


def create_message(sentiment, score, nifty, banknifty):

    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(banknifty["change"])

    msg = "🚀 *INSTITUTIONAL PRE-MARKET ENGINE v2.1*\n\n"

    msg += f"🌍 Global Sentiment: *{sentiment}*\n\n"

    msg += "📊 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}* ({nifty['change']:.2f}%)\n"
    msg += f"• BANKNIFTY: *{bank_bias}* ({banknifty['change']:.2f}%)\n\n"

    msg += "📦 Market Behaviour:\n"

    if nifty_bias == bank_bias:
        msg += f"• Trend Day Expected ({nifty_bias})\n"
    else:
        msg += "• Mixed / Stock Specific Day\n"

    msg += "\n⚠️ Informational only. No investment advice."
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:

        print("🚀 Running Institutional Engine v2.1")

        sentiment, score = get_global_sentiment()

        nifty = get_index_data("NIFTY 50", "^NSEI")
        banknifty = get_index_data("NIFTY BANK", "^NSEBANK")

        if not nifty or not banknifty:
            send_telegram("⚠️ Market data unavailable")
        else:
            msg = create_message(sentiment, score, nifty, banknifty)
            send_telegram(msg)

        print("✅ Done")

    except Exception as e:
        print("❌ Fatal Error:", e)
