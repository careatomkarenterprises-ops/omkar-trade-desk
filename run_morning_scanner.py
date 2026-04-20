import requests
import json
from datetime import datetime
import os

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
# NSE PRE-OPEN DATA
# ============================
def fetch_preopen_data():
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)

    response = session.get(url, headers=headers)
    data = response.json()

    return data["data"]

# ============================
# PROCESS DATA
# ============================
def process_data(data):
    stocks = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta["symbol"]
            price = meta["iep"]  # Indicative Equilibrium Price
            change = meta["pChange"]

            if price > 0:
                stocks.append((symbol, change, price))

        except:
            continue

    # Sort
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
        gainers, losers = process_data(data)
        message = create_message(gainers, losers)

        send_telegram(message)

        print("✅ Pre-market data sent successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
