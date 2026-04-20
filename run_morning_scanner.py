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
# FETCH NSE PRE-OPEN
# ============================
def fetch_preopen_data():
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    time.sleep(1)

    try:
        res = session.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json().get("data", [])
    except:
        pass

    return []


# ============================
# TRADE GENERATOR
# ============================
def generate_trade(symbol, change, price):
    if change > 0:
        return f"{symbol} (BUY) | ₹{price} | +{change:.2f}%"
    else:
        return f"{symbol} (SELL) | ₹{price} | {change:.2f}%"


# ============================
# PROCESS
# ============================
def process_data(data):
    strong = []
    weak = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            if not symbol.isalpha() or price <= 0:
                continue

            # Strong movers
            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            # Weak movers (fallback)
            elif abs(change) > 0.5:
                weak.append((symbol, change, price))

        except:
            continue

    strong = sorted(strong, key=lambda x: abs(x[1]), reverse=True)[:5]
    weak = sorted(weak, key=lambda x: abs(x[1]), reverse=True)[:5]

    return strong, weak, len(data)


# ============================
# MESSAGE
# ============================
def create_message(strong, weak, total):
    msg = "📊 *PRE-MARKET SCANNER (NSE DATA)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Source: NSE Pre-Open Market\n\n"

    if strong:
        msg += "🚀 *Strong Movers (Trade Focus)*\n"
        for s in strong:
            msg += f"• {generate_trade(*s)}\n"
    else:
        msg += "⚠️ No strong movers today\n"

    if weak:
        msg += "\n📉 *Weak Movers (Watchlist)*\n"
        for s in weak:
            msg += f"• {generate_trade(*s)}\n"

    msg += "\n\n🧠 Market Insight:\n"
    if not strong:
        msg += "Low volatility — avoid aggressive trades\n"
    else:
        msg += "Momentum present — watch breakouts after 9:20\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        data = fetch_preopen_data()

        if not data:
            raise Exception("No data from NSE")

        strong, weak, total = process_data(data)

        message = create_message(strong, weak, total)

        send_telegram(message)

        print("✅ Sent successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
