import requests
from datetime import datetime
import os
import time

from src.scanner.volume_analyzer import VolumeSetupAnalyzer
from src.scanner.data_fetcher import fetch_historical_data

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")

analyzer = VolumeSetupAnalyzer()


# ============================
# TELEGRAM
# ============================
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print(f"Telegram error: {e}")


# ============================
# NSE PREOPEN FETCH
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
# PROCESS WITH SMART MONEY
# ============================
def process_data(data):

    strong = []
    watchlist = []
    smart_money = []

    for item in data:

        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            if not symbol or price <= 0:
                continue

            # Normal logic (UNCHANGED)
            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            elif abs(change) > 0.7:
                watchlist.append((symbol, change, price))

            # ============================
            # SMART MONEY (REAL DATA)
            # ============================
            df = fetch_historical_data(symbol, "30minute", 5)

            if df is not None and not df.empty:

                score, label = analyzer.smart_money_score(df)

                if score >= 55:
                    smart_money.append((symbol, price, change, score, label))

        except:
            continue

    strong = sorted(strong, key=lambda x: abs(x[1]), reverse=True)[:5]
    watchlist = sorted(watchlist, key=lambda x: abs(x[1]), reverse=True)[:5]
    smart_money = sorted(smart_money, key=lambda x: x[3], reverse=True)[:5]

    return strong, watchlist, smart_money, len(data)


# ============================
# MESSAGE BUILDER
# ============================
def create_message(strong, watchlist, smart, total):

    msg = "📊 *PRE-MARKET INSIGHT (SMART MONEY)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data: NSE Pre-Open + 30m Volume Flow\n\n"

    # SMART MONEY
    if smart:
        msg += "🔥 *SMART MONEY ACCUMULATION*\n"
        for s in smart:
            msg += f"• {s[0]} | Score: {s[3]:.0f}\n"
            msg += f"  ₹{s[1]} | {s[4]}\n\n"
    else:
        msg += "⚠️ No smart money accumulation detected\n\n"

    # MOVERS
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

    msg += "\n⚠️ Educational Only"
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
