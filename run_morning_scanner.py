import requests
from datetime import datetime
import os
import time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")


# ============================
# TELEGRAM
# ============================
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")


# ============================
# FETCH NSE PREOPEN
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

    except:
        pass

    return []


# ============================
# SMART MONEY SCORE ENGINE 🔥
# ============================
def calculate_smart_score(price, change):

    score = 0

    # 1. Momentum score (30)
    if abs(change) > 2:
        score += 30
    elif abs(change) > 1:
        score += 20
    elif abs(change) > 0.5:
        score += 10

    # 2. Direction bias (20)
    if change > 0:
        score += 20

    # 3. Volatility strength (20)
    if abs(change) > 1.5:
        score += 20
    elif abs(change) > 0.8:
        score += 10

    # 4. Price structure zone (30)
    if price > 500:
        score += 20
    elif price > 100:
        score += 15
    else:
        score += 10

    return min(score, 100)


# ============================
# PROCESS DATA
# ============================
def process_data(data):

    strong = []
    watchlist = []
    smart = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            if not symbol or price <= 0:
                continue

            # existing logic (UNCHANGED)
            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            elif abs(change) > 0.7:
                watchlist.append((symbol, change, price))

            # SMART MONEY SCORE
            score = calculate_smart_score(price, change)

            if score >= 70:
                smart.append((symbol, price, change, score))

        except:
            continue

    strong = sorted(strong, key=lambda x: abs(x[1]), reverse=True)[:5]
    watchlist = sorted(watchlist, key=lambda x: abs(x[1]), reverse=True)[:5]
    smart = sorted(smart, key=lambda x: x[3], reverse=True)[:5]

    return strong, watchlist, smart, len(data)


# ============================
# MESSAGE BUILDER
# ============================
def create_message(strong, watchlist, smart, total):

    msg = "📊 *PRE-MARKET INSIGHT (SMART MONEY SCORE)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data Source: NSE Pre-Open\n\n"

    # SMART MONEY SECTION
    if smart:
        msg += "🔥 *SMART MONEY ALERTS*\n"
        for s in smart:
            direction = "Bullish" if s[2] > 0 else "Bearish"
            msg += f"• {s[0]} – SCORE: {s[3]}/100\n"
            msg += f"  ₹{s[1]} | {direction}\n\n"
    else:
        msg += "⚠️ No strong smart money setups\n\n"

    # NORMAL MOVERS
    if strong:
        msg += "🚀 High Momentum Stocks\n"
        for s in strong:
            msg += f"• {s[0]} | ₹{s[2]} | {s[1]:.2f}%\n"
    else:
        msg += "⚠️ No strong movers\n"

    # WATCHLIST
    if watchlist:
        msg += "\n📉 Watchlist\n"
        for s in watchlist:
            msg += f"• {s[0]} | ₹{s[2]} | {s[1]:.2f}%\n"

    msg += "\n⚠️ Educational purpose only"
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        data = fetch_preopen_data()

        if not data:
            send_telegram("⚠️ No pre-open data received")
            exit()

        strong, watchlist, smart, total = process_data(data)

        message = create_message(strong, watchlist, smart, total)

        send_telegram(message)

        print("✅ Morning Scanner Completed")

    except Exception as e:
        send_telegram(f"❌ Error: {e}")
        print(e)
