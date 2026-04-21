import requests
from datetime import datetime
import os
import time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")


# ============================
# TELEGRAM SAFE
# ============================
def send_telegram(message):
    try:
        if not BOT_TOKEN or not CHANNEL:
            print("Missing Telegram credentials")
            return

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=payload, timeout=10)

    except Exception as e:
        print(f"Telegram error: {e}")


# ============================
# NSE FETCH (SAFE MODE)
# ============================
def fetch_preopen_data():
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()

    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        time.sleep(1)

        res = session.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            return res.json().get("data", [])

    except Exception as e:
        print(f"Fetch error: {e}")

    return []


# ============================
# PROCESS + CLEAN DATA
# ============================
def process_data(data):
    strong = []
    watchlist = []

    for item in data:
        try:
            meta = item.get("metadata", {})

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            if not symbol or price <= 0:
                continue

            # STRONG MOMENTUM
            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            # WATCHLIST ZONE
            elif abs(change) > 0.7:
                watchlist.append((symbol, change, price))

        except:
            continue

    strong = sorted(strong, key=lambda x: abs(x[1]), reverse=True)[:5]
    watchlist = sorted(watchlist, key=lambda x: abs(x[1]), reverse=True)[:5]

    return strong, watchlist, len(data)


# ============================
# SMART BIAS ENGINE (UPGRADED)
# ============================
def get_market_bias(strong, watchlist):
    total = len(strong) + len(watchlist)

    if total == 0:
        return "LOW VOLATILITY / SIDEWAYS"

    bullish = len([s for s in strong if s[1] > 0])
    bearish = len([s for s in strong if s[1] < 0])

    if bullish > bearish:
        return "BULLISH ACCUMULATION"
    elif bearish > bullish:
        return "BEARISH DISTRIBUTION"
    else:
        return "MIXED FLOW"


# ============================
# MESSAGE ENGINE (UPGRADED INTELLIGENCE)
# ============================
def create_message(strong, watchlist, total):

    msg = "📊 *PRE-MARKET INSIGHT (NSE)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data Source: NSE Pre-Open\n"

    bias = get_market_bias(strong, watchlist)
    msg += f"📊 Market Bias: *{bias}*\n\n"

    # STRONG ZONE
    if strong:
        msg += "🚀 *High Momentum Stocks*\n"
        for s in strong:
            direction = "Positive" if s[1] > 0 else "Negative"
            msg += f"• {s[0]} | ₹{s[2]} | {direction} ({s[1]:.2f}%)\n"
    else:
        msg += "⚠️ No strong movers detected\n"

    # WATCHLIST ZONE
    if watchlist:
        msg += "\n📉 *Watchlist (Early Interest)*\n"
        for s in watchlist:
            direction = "Positive" if s[1] > 0 else "Negative"
            msg += f"• {s[0]} | ₹{s[2]} | {direction} ({s[1]:.2f}%)\n"

    # SMART INSIGHT LAYER (NEW)
    msg += "\n🧠 *AI Insight Layer*\n"

    if strong:
        msg += "⚡ Momentum detected in select stocks.\n"
        msg += "📌 Watch breakout after 9:15 confirmation.\n"
    else:
        msg += "⚠️ No institutional pre-open buildup detected.\n"
        msg += "📌 Expect range-bound open.\n"

    msg += "\n⚠️ Educational purpose only\n"
    msg += f"⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN SAFE EXECUTION
# ============================
if __name__ == "__main__":

    try:
        data = fetch_preopen_data()

        if not data:
            send_telegram(
                "⚠️ *Morning Scanner*\n\n"
                "No NSE pre-open data received.\n"
                "System executed safely."
            )
            print("No data received")
            exit()

        strong, watchlist, total = process_data(data)

        message = create_message(strong, watchlist, total)

        send_telegram(message)

        print("✅ Morning Scanner Completed")

    except Exception as e:
        send_telegram(f"❌ Morning Scanner Error: {e}")
        print(e)
