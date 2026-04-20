import requests
import json
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
# NSE PRE-OPEN DATA (SAFE FETCH)
# ============================
def fetch_preopen_data():
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive"
    }

    session = requests.Session()

    # Step 1: Load homepage (IMPORTANT for cookies)
    session.get("https://www.nseindia.com", headers=headers)
    time.sleep(1)

    # Step 2: Retry logic
    for attempt in range(3):
        try:
            response = session.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"⚠ Attempt {attempt+1}: Status {response.status_code}")
                time.sleep(2)
                continue

            data = response.json()
            return data.get("data", [])

        except Exception as e:
            print(f"⚠ Attempt {attempt+1} failed: {e}")
            time.sleep(2)

    raise Exception("Failed to fetch NSE data after retries")

# ============================
# PROCESS DATA
# ============================
def process_data(data):
    stocks = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            # ✅ FILTER ONLY EQUITY (REMOVE BONDS / SG / NCD)
            if (
                price > 0 and
                symbol.isalpha() and   # removes 704WB35-SG type
                len(symbol) <= 15
            ):
                stocks.append((symbol, change, price))

        except:
            continue

    # Sort by % change
    stocks = sorted(stocks, key=lambda x: x[1], reverse=True)

    return stocks[:5], stocks[-5:]

# ============================
# FORMAT MESSAGE
# ============================
def create_message(gainers, losers):
    msg = "📊 *PRE-MARKET SCANNER (NSE)*\n\n"

    msg += "🚀 *Top Gainers*\n"
    for s in gainers:
        msg += f"• {s[0]} | +{s[1]:.2f}% | ₹{s[2]}\n"

    msg += "\n🔻 *Top Losers*\n"
    for s in losers:
        msg += f"• {s[0]} | {s[1]:.2f}% | ₹{s[2]}\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg

# ============================
# RUN
# ============================
if __name__ == "__main__":
    try:
        data = fetch_preopen_data()

        if not data:
            raise Exception("Empty data received from NSE")

        gainers, losers = process_data(data)
        message = create_message(gainers, losers)

        send_telegram(message)

        print("✅ Pre-market data sent successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
