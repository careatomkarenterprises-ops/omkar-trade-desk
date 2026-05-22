import requests
import os
import time
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
PREMIUM_CHANNEL = os.getenv("CHANNEL_PREMIUM")


# =========================
# TELEGRAM
# =========================
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
            timeout=10
        )

    except Exception as e:
        print(f"Telegram Error: {e}")


# =========================
# FETCH NSE PREOPEN
# =========================
def fetch():

    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()

    try:
        session.get(
            "https://www.nseindia.com",
            headers=headers,
            timeout=5
        )

        time.sleep(1)

        res = session.get(
            url,
            headers=headers,
            timeout=10
        )

        return res.json().get("data", [])

    except Exception as e:
        print(f"NSE Fetch Error: {e}")
        return []


# =========================
# PROCESS DATA
# =========================
def analyze(data):

    stocks = []

    for item in data:

        try:
            m = item["metadata"]

            symbol = m["symbol"]
            change = float(m["pChange"])
            price = float(m["iep"])

            if price <= 0:
                continue

            # Probability score
            score = min(100, abs(change) * 20)

            if score >= 40:

                stocks.append({
                    "symbol": symbol,
                    "change": change,
                    "price": price,
                    "score": int(score)
                })

        except Exception:
            continue

    return sorted(
        stocks,
        key=lambda x: x["score"],
        reverse=True
    )[:6]


# =========================
# BUILD TELEGRAM MESSAGE
# =========================
def build_messages(stocks):

    # FREE VERSION
    free_msg = "📊 *PRE-OPEN STOCK WATCH*\n\n"

    for s in stocks[:3]:

        free_msg += (
            f"• {s['symbol']} | "
            f"{s['change']:.2f}%\n"
        )

    free_msg += "\n🔒 Full levels & entries in premium"

    free_msg += (
        f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    )

    # PREMIUM VERSION
    premium_msg = "🔥 *SMART MONEY STOCKS (PRE-OPEN)*\n\n"

    for s in stocks:

        premium_msg += (
            f"• {s['symbol']} | "
            f"₹{s['price']} | "
            f"{s['change']:.2f}% | "
            f"Score: {s['score']}\n"
        )

    premium_msg += "\n📌 Plan: Wait for breakout confirmation"
    premium_msg += "\n⚠️ Informational only"

    return free_msg, premium_msg


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    print("🚀 Starting Pre-Open Scanner")

    data = fetch()

    if not data:

        send(
            "⚠️ Pre-open data unavailable",
            FREE_CHANNEL
        )

        print("❌ No NSE Data")
        exit()

    stocks = analyze(data)

    if not stocks:

        print("❌ No Stocks Found")
        exit()

    free_msg, premium_msg = build_messages(stocks)

    # PREMIUM FIRST
    send(premium_msg, PREMIUM_CHANNEL)

    print("✅ Premium Sent")

    # DELAY FREE VERSION
    time.sleep(120)

    send(free_msg, FREE_CHANNEL)

    print("✅ Free Channel Sent")

    print("🎯 Scanner Completed")
