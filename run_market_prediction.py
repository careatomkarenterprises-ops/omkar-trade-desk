import requests
import os
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_CHANNELS = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
]

PREMIUM_CHANNELS = [
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

# ============================
# TELEGRAM
# ============================
def send(channels, message):
    for ch in channels:
        if not ch:
            continue
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={
                "chat_id": ch,
                "text": message,
                "parse_mode": "Markdown"
            })
            print(f"✅ Sent to {ch}")
        except Exception as e:
            print("Telegram Error:", e)


# ============================
# FETCH (YAHOO - STABLE)
# ============================
def fetch(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        data = requests.get(url, timeout=10).json()

        meta = data["chart"]["result"][0]["meta"]

        ltp = meta["regularMarketPrice"]
        prev = meta["previousClose"]

        change = ((ltp - prev) / prev) * 100

        return {"ltp": ltp, "change": change}
    except:
        return None


# ============================
# GLOBAL SENTIMENT
# ============================
def global_sentiment():
    spx = fetch("^GSPC")
    if not spx:
        return "MIXED"

    if spx["change"] > 0.5:
        return "POSITIVE"
    elif spx["change"] < -0.5:
        return "NEGATIVE"
    return "MIXED"


# ============================
# GAP LOGIC
# ============================
def gap_logic(nifty_change, sentiment):
    score = 0

    if nifty_change > 0.5:
        score += 1
    elif nifty_change < -0.5:
        score -= 1

    if sentiment == "POSITIVE":
        score += 1
    elif sentiment == "NEGATIVE":
        score -= 1

    mapping = {
        2: "HIGH GAP-UP",
        1: "MILD GAP-UP",
        0: "FLAT OPEN",
        -1: "MILD GAP-DOWN",
        -2: "HIGH GAP-DOWN"
    }

    return mapping.get(score, "FLAT OPEN")


# ============================
# BIAS
# ============================
def bias(change):
    if change > 0.4:
        return "BULLISH"
    elif change < -0.4:
        return "BEARISH"
    return "SIDEWAYS"


# ============================
# FREE MESSAGE (FUNNEL ENTRY)
# ============================
def free_msg(global_s, gap, nb, bb):
    return f"""🌅 *PRE-MARKET SNAPSHOT*

🌍 Global: *{global_s}*
📊 NIFTY: *{nb}*
🏦 BANK NIFTY: *{bb}*
⚡ Gap: *{gap}*

📌 Plan:
• Wait for 9:20 confirmation
• Avoid early entries

🔥 Premium = Exact entry levels + live trades

⏰ {datetime.now().strftime('%H:%M:%S')}
"""


# ============================
# PREMIUM MESSAGE (VALUE)
# ============================
def premium_msg(global_s, gap, nifty, bank):
    nb = bias(nifty["change"])
    bb = bias(bank["change"])

    return f"""🏦 *INSTITUTIONAL PRE-MARKET REPORT*

🌍 Sentiment: *{global_s}*
⚡ Gap Outlook: *{gap}*

📊 Index Bias:
• NIFTY: *{nb}* ({round(nifty['change'],2)}%)
• BANK: *{bb}* ({round(bank['change'],2)}%)

📦 Strategy:
• {"Buy on dips" if nb=="BULLISH" else "Sell on rise" if nb=="BEARISH" else "Range trade"}
• Wait first 15-min breakout

🎯 9:20 Rule:
• Above high → LONG
• Below low → SHORT

⏰ {datetime.now().strftime('%H:%M:%S')}

⚠️ Informational only
"""


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("🚀 Running Pre-Market System")

    nifty = fetch("^NSEI")
    bank = fetch("^NSEBANK")

    if not nifty or not bank:
        send(FREE_CHANNELS + PREMIUM_CHANNELS, "⚠️ Data unavailable")
        exit()

    gs = global_sentiment()
    gap = gap_logic(nifty["change"], gs)

    nb = bias(nifty["change"])
    bb = bias(bank["change"])

    send(FREE_CHANNELS, free_msg(gs, gap, nb, bb))
    send(PREMIUM_CHANNELS, premium_msg(gs, gap, nifty, bank))

    print("✅ Done")
