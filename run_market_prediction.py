import requests
import os
import time
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNEL_FREE = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
]

CHANNEL_PREMIUM = [
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

# ============================
# TELEGRAM
# ============================
def send_message(message, channels):
    for ch in channels:
        if not ch:
            continue
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": ch,
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, data=payload, timeout=10)
            print(f"✅ Sent to {ch}")
        except Exception as e:
            print("Telegram Error:", e)


# ============================
# NSE FETCH (STABLE)
# ============================
def fetch_price(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    try:
        res = requests.get(url, timeout=10).json()

        result = res["chart"]["result"][0]
        close = result["meta"]["regularMarketPrice"]
        prev = result["meta"]["previousClose"]

        return {
            "current": close,
            "prev_close": prev,
            "change": ((close - prev) / prev) * 100
        }

    except Exception as e:
        print("❌ Fetch failed:", e)
        return None


# ============================
# GLOBAL SENTIMENT (SIMPLE)
# ============================
def get_global_sentiment():
    try:
        spx = fetch_price("^GSPC")
        if not spx:
            return "MIXED"

        if spx["change"] > 0.5:
            return "POSITIVE"
        elif spx["change"] < -0.5:
            return "NEGATIVE"
        else:
            return "MIXED"
    except:
        return "MIXED"


# ============================
# GAP PROBABILITY LOGIC
# ============================
def gap_probability(nifty_change, global_sentiment):
    score = 0

    # NIFTY momentum
    if nifty_change > 0.5:
        score += 1
    elif nifty_change < -0.5:
        score -= 1

    # Global sentiment
    if global_sentiment == "POSITIVE":
        score += 1
    elif global_sentiment == "NEGATIVE":
        score -= 1

    if score >= 2:
        return "HIGH GAP-UP"
    elif score == 1:
        return "MILD GAP-UP"
    elif score == 0:
        return "FLAT OPEN"
    elif score == -1:
        return "MILD GAP-DOWN"
    else:
        return "HIGH GAP-DOWN"


# ============================
# BIAS
# ============================
def get_bias(change):
    if change > 0.4:
        return "BULLISH"
    elif change < -0.4:
        return "BEARISH"
    return "SIDEWAYS"


# ============================
# FREE MESSAGE
# ============================
def create_free_msg(global_sentiment, gap, nifty_bias, bank_bias):
    msg = "🌅 *PRE-MARKET SNAPSHOT*\n\n"

    msg += f"🌍 Global: *{global_sentiment}*\n"
    msg += f"📊 NIFTY: *{nifty_bias}*\n"
    msg += f"🏦 BANK NIFTY: *{bank_bias}*\n"
    msg += f"⚡ Gap Expectation: *{gap}*\n\n"

    msg += "📌 *Plan:*\n"
    msg += "• Wait for 9:20 confirmation\n"
    msg += "• Avoid early entries\n\n"

    msg += "🔐 Premium gives exact levels & trade plan\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# PREMIUM MESSAGE
# ============================
def create_premium_msg(global_sentiment, gap, nifty, bank):
    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(bank["change"])

    msg = "🏦 *INSTITUTIONAL PRE-MARKET REPORT*\n\n"

    msg += f"🌍 Global Sentiment: *{global_sentiment}*\n"
    msg += f"⚡ Gap Outlook: *{gap}*\n\n"

    msg += "📊 Index Bias:\n"
    msg += f"• NIFTY: *{nifty_bias}* ({round(nifty['change'],2)}%)\n"
    msg += f"• BANK NIFTY: *{bank_bias}* ({round(bank['change'],2)}%)\n\n"

    msg += "📦 Expected Behaviour:\n"

    if nifty_bias == "BULLISH":
        msg += "• Buy on dips strategy\n"
    elif nifty_bias == "BEARISH":
        msg += "• Sell on rise strategy\n"
    else:
        msg += "• Range-bound day\n"

    msg += "• Wait first 15-min breakout\n"
    msg += "• Avoid fake breakout traps\n\n"

    msg += "🎯 *9:20 Confirmation Rule:*\n"
    msg += "• Above opening high → LONG\n"
    msg += "• Below opening low → SHORT\n\n"

    msg += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    msg += "\n\n⚠️ Informational only"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("🚀 Running PRO Market System...")

    nifty = fetch_price("^NSEI")
    bank = fetch_price("^NSEBANK")

    if not nifty or not bank:
        send_message("⚠️ Market data unavailable", CHANNEL_FREE + CHANNEL_PREMIUM)
        exit()

    global_sentiment = get_global_sentiment()
    gap = gap_probability(nifty["change"], global_sentiment)

    nifty_bias = get_bias(nifty["change"])
    bank_bias = get_bias(bank["change"])

    # FREE
    free_msg = create_free_msg(global_sentiment, gap, nifty_bias, bank_bias)
    send_message(free_msg, CHANNEL_FREE)

    # PREMIUM
    premium_msg = create_premium_msg(global_sentiment, gap, nifty, bank)
    send_message(premium_msg, CHANNEL_PREMIUM)

    print("✅ Done")
