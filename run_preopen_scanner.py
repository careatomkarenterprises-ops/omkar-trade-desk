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

        response = requests.post(
            url,
            data={
                "chat_id": channel,
                "text": msg,
                "parse_mode": "Markdown"
            },
            timeout=20
        )

        if response.status_code == 200:
            print(f"✅ Telegram Message Sent -> {channel}")
        else:
            print(f"❌ Telegram Error Code: {response.status_code}")

    except Exception as e:
        print(f"❌ Telegram Exception: {e}")


# =========================================
# NSE PREOPEN FETCH
# =========================================
def fetch_preopen_data():

    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

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

    # Retry NSE 3 Times
    for attempt in range(3):

        try:

            print(f"🔄 NSE Fetch Attempt: {attempt + 1}")

            session = requests.Session()

            # Load homepage first for cookies
            session.get(
                "https://www.nseindia.com",
                headers=headers,
                timeout=20
            )

            time.sleep(3)

            # Fetch API
            response = session.get(
                url,
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:

                print(f"❌ NSE Status Code: {response.status_code}")

                time.sleep(5)
                continue

            data = response.json()

            records = data.get("data", [])

            if records:

                print(f"✅ NSE Data Records: {len(records)}")

                return records

            print("⚠ Empty NSE Data")

        except Exception as e:

            print(f"❌ NSE Fetch Error: {e}")

        time.sleep(5)

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

            # Smart scoring logic
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

    # FREE MESSAGE
    free_msg = "📊 *PRE-OPEN STOCK WATCH*\\n\\n"

    for s in stocks[:3]:

        free_msg += (
            f"• {s['symbol']} | "
            f"{s['change']:.2f}%\\n"
        )

    free_msg += "\\n🔒 Full setup in premium"
    free_msg += f"\\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    # PREMIUM MESSAGE
    premium_msg = "🔥 *SMART MONEY PRE-OPEN STOCKS*\\n\\n"

    for s in stocks:

        premium_msg += (
            f"• {s['symbol']} | "
            f"₹{s['price']} | "
            f"{s['change']:.2f}% | "
            f"Score: {s['score']}\\n"
        )

    premium_msg += "\\n📌 Wait for breakout confirmation"
    premium_msg += "\\n⚠️ Educational Purpose Only"

    return free_msg, premium_msg


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    print("=======================================")
    print("🚀 STARTING PRE-OPEN SCANNER")
    print("=======================================")

    data = fetch_preopen_data()

    if not data:

        print("❌ NO NSE DATA AVAILABLE")

        send(
            "⚠️ NSE Pre-open data unavailable today",
            FREE_CHANNEL
        )

        exit()

    stocks = analyze(data)

    if not stocks:

        print("❌ NO VALID STOCKS FOUND")

        send(
            "⚠️ No strong pre-open setups today",
            FREE_CHANNEL
        )

        exit()

    print(f"✅ Final Stocks Selected: {len(stocks)}")

    free_msg, premium_msg = build_messages(stocks)

    print("📤 Sending Premium Message")

    send(
        premium_msg,
        PREMIUM_CHANNEL
    )

    print("⏳ Waiting 120 seconds before Free Signal")

    time.sleep(120)

    print("📤 Sending Free Message")

    send(
        free_msg,
        FREE_CHANNEL
    )

    print("=======================================")
    print("✅ PRE-OPEN SCANNER COMPLETED")
    print("=======================================")
```
