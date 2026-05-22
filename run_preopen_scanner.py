import requests
import os
import time
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
PREMIUM_CHANNEL = os.getenv("CHANNEL_PREMIUM")


# =========================================
# TELEGRAM SENDER
# =========================================
def send(msg, channel):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(
            url,
            data={
                "chat_id": channel,
                "text": msg,
                "parse_mode": "Markdown"
            },
            timeout=15
        )

        print(f"✅ Sent message to {channel}")

    except Exception as e:
        print(f"Telegram Error: {e}")


# =========================================
# NSE PREOPEN FETCH
# =========================================
def fetch_preopen_data():

    session = requests.Session()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive"
    }

    try:

        # STEP 1: Load NSE Homepage
        session.get(
            "https://www.nseindia.com",
            headers=headers,
            timeout=20
        )

        time.sleep(3)

        # STEP 2: Fetch Preopen Data
        url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

        response = session.get(
            url,
            headers=headers,
            timeout=20
        )

        if response.status_code != 200:
            print(f"NSE Status Code: {response.status_code}")
            return []

        data = response.json()

        return data.get("data", [])

    except Exception as e:
        print(f"NSE Fetch Error: {e}")
        return []


# =========================================
# ANALYZE STOCKS
# =========================================
def analyze(data):

    stocks = []

    for item in data:

        try:
            meta = item["metadata"]

            symbol = meta["symbol"]
            change = float(meta["pChange"])
            price = float(meta["iep"])

            if price <= 0:
                continue

            score = min(100, abs(change) * 20)

            if score >= 40:

                stocks.append({
                    "symbol": symbol,
                    "change": change,
                    "price": price,
                    "score": int(score)
                })

        except:
            continue

    return sorted(
        stocks,
        key=lambda x: x["score"],
        reverse=True
    )[:6]


# =========================================
# BUILD TELEGRAM MESSAGE
# =========================================
def build_messages(stocks):

    free_msg = "📊 *PRE-OPEN STOCK WATCH*\n\n"

    for s in stocks[:3]:

        free_msg += (
            f"• {s['symbol']} | "
            f"{s['change']:.2f}%\n"
        )

    free_msg += "\n🔒 Full setup in premium"
    free_msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    premium_msg = "🔥 *SMART MONEY PRE-OPEN STOCKS*\n\n"

    for s in stocks:

        premium_msg += (
            f"• {s['symbol']} | "
            f"₹{s['price']} | "
            f"{s['change']:.2f}% | "
            f"Score: {s['score']}\n"
        )

    premium_msg += "\n📌 Wait for breakout confirmation"
    premium_msg += "\n⚠️ Educational Purpose Only"

    return free_msg, premium_msg


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    print("🚀 Starting Pre-Open Scanner")

    data = fetch_preopen_data()

    if not data:

        print("❌ No NSE Data")

        send(
            "⚠️ NSE Pre-open data unavailable",
            FREE_CHANNEL
        )

        exit()

    print(f"✅ NSE Records Fetched: {len(data)}")

    stocks = analyze(data)

    if not stocks:

        print("❌ No Stocks Found")

        send(
            "⚠️ No valid pre-open setups today",
            FREE_CHANNEL
        )

        exit()

    free_msg, premium_msg = build_messages(stocks)

    print("📤 Sending Premium Message")

    send(premium_msg, PREMIUM_CHANNEL)

    print("⏳ Waiting before Free Message")

    time.sleep(120)

    print("📤 Sending Free Message")

    send(free_msg, FREE_CHANNEL)

    print("✅ Pre-Open Scanner Completed")
