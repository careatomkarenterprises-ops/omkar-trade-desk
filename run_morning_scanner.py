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
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

# ============================
# NSE PRE-OPEN FETCH
# ============================
def fetch_preopen_data():
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive"
    }

    session = requests.Session()

    # Load NSE homepage (important for cookies)
    session.get("https://www.nseindia.com", headers=headers)
    time.sleep(1)

    for i in range(3):
        try:
            res = session.get(url, headers=headers, timeout=10)

            if res.status_code != 200:
                time.sleep(2)
                continue

            return res.json().get("data", [])

        except:
            time.sleep(2)

    return []

# ============================
# PROCESS DATA (FILTERED)
# ============================
def process_data(data):
    stocks = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            # ✅ Filters (IMPORTANT)
            if (
                price > 100 and              # avoid penny stocks
                abs(change) > 1.5 and        # only strong movers
                symbol.isalpha()             # remove bonds like 704WB35-SG
            ):
                stocks.append((symbol, change, price))

        except:
            continue

    stocks = sorted(stocks, key=lambda x: x[1], reverse=True)

    gainers = [s for s in stocks if s[1] > 0][:5]
    losers = [s for s in stocks if s[1] < 0][-5:]

    return gainers, losers

# ============================
# FORMAT MESSAGE (PREMIUM STYLE)
# ============================
def create_message(gainers, losers):
    msg = "📊 *PRE-MARKET TRADE SETUPS (NSE)*\n\n"

    if gainers:
        msg += "🚀 *Bullish Watchlist*\n"
        for s in gainers:
            msg += f"• {s[0]} (+{s[1]:.2f}%) | ₹{s[2]}\n"

    if losers:
        msg += "\n🔻 *Bearish Watchlist*\n"
        for s in losers:
            msg += f"• {s[0]} ({s[1]:.2f}%) | ₹{s[2]}\n"

    msg += "\n\n⚠️ *Wait for breakout after 9:20 AM*\n"
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg

# ============================
# MAIN RUN
# ============================
if __name__ == "__main__":
    try:
        data = fetch_preopen_data()

        if not data:
            raise Exception("No data received from NSE")

        gainers, losers = process_data(data)

        if not gainers and not losers:
            send_telegram("⚠️ No strong pre-market setups found today.")
            print("No setups")
        else:
            message = create_message(gainers, losers)
            send_telegram(message)
            print("✅ Sent successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
