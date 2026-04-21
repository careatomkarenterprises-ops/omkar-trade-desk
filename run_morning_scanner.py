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
# NSE PREOPEN DATA
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
        print(f"NSE fetch error: {e}")

    return []


# ============================
# SMART MONEY v2 ENGINE (STABLE)
# ============================
def calculate_smart_score(price, change, volume=None):

    score = 0

    # 1. Momentum strength
    if abs(change) > 2:
        score += 35
    elif abs(change) > 1:
        score += 25
    elif abs(change) > 0.5:
        score += 15

    # 2. Direction confirmation
    if change > 0:
        score += 20

    # 3. Price structure strength
    if price > 500:
        score += 20
    elif price > 100:
        score += 15
    else:
        score += 10

    # 4. Intraday accumulation proxy (IMPORTANT FIX)
    if abs(change) > 1.2:
        score += 25

    return min(score, 100)


# ============================
# PROCESS DATA
# ============================
def process_data(data):

    strong = []
    watchlist = []
    smart = []
    symbols = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            if not symbol or price <= 0:
                continue

            symbols.append(symbol)

            # NORMAL MOVERS
            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            elif abs(change) > 0.7:
                watchlist.append((symbol, change, price))

            # SMART MONEY LOGIC (FIXED)
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

    msg = "📊 *PRE-MARKET INSIGHT (SMART MONEY v2)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data Source: NSE Pre-Open Engine\n\n"

    # SMART MONEY SECTION
    if smart:
        msg += "🔥 *SMART MONEY ACCUMULATION*\n"
        for s in smart:
            level = "STRONG" if s[3] >= 80 else "MODERATE"
            msg += f"• {s[0]} | Score: {s[3]} | {level}\n"
    else:
        msg += "⚠️ No smart money accumulation detected\n"

    # MOVERS
    if strong:
        msg += "\n🚀 High Momentum Stocks\n"
        for s in strong:
            msg += f"• {s[0]} | ₹{s[2]} | {s[1]:.2f}%\n"

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
