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
# FETCH NSE PRE-OPEN DATA
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
        print(f"Fetch error: {e}")

    return []


# ============================
# PROCESS DATA
# ============================
def process_data(data):
    strong = []
    watchlist = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            if not symbol or price <= 0:
                continue

            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            elif abs(change) > 0.7:
                watchlist.append((symbol, change, price))

        except:
            continue

    strong = sorted(strong, key=lambda x: abs(x[1]), reverse=True)[:5]
    watchlist = sorted(watchlist, key=lambda x: abs(x[1]), reverse=True)[:5]

    return strong, watchlist, len(data)


# ============================
# MARKET BIAS
# ============================
def get_market_bias(strong):
    if not strong:
        return "SIDEWAYS / LOW MOMENTUM"

    bullish = len([s for s in strong if s[1] > 0])
    bearish = len([s for s in strong if s[1] < 0])

    if bullish > bearish:
        return "BULLISH BIAS"
    elif bearish > bullish:
        return "BEARISH BIAS"
    else:
        return "MIXED / SIDEWAYS"


# ============================
# MESSAGE
# ============================
def create_message(strong, watchlist, total):
    msg = "📊 *PRE-MARKET INSIGHT (NSE)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data Source: NSE Pre-Open\n"

    bias = get_market_bias(strong)
    msg += f"📊 Market Bias: *{bias}*\n\n"

    if strong:
        msg += "🚀 *High Momentum Stocks*\n"
        for s in strong:
            direction = "Positive" if s[1] > 0 else "Negative"
            msg += f"• {s[0]} | ₹{s[2]} | {direction} ({s[1]:.2f}%)\n"
    else:
        msg += "⚠️ No strong movers\n"

    if watchlist:
        msg += "\n📉 *Watchlist*\n"
        for s in watchlist:
            direction = "Positive" if s[1] > 0 else "Negative"
            msg += f"• {s[0]} | ₹{s[2]} | {direction} ({s[1]:.2f}%)\n"

    msg += "\n⚠️ Educational purpose only"
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN (FIXED SAFE VERSION)
# ============================
if __name__ == "__main__":
    try:
        data = fetch_preopen_data()

        # ✅ SAFE FIX (NO CRASH)
        if not data:
            send_telegram(
                "⚠️ *Morning Scanner Alert*\n\n"
                "No pre-open data received from NSE.\n"
                "Market may be inactive or blocked.\n"
                "System ran successfully but no data available."
            )
            print("No data - fallback message sent")
            exit()

        strong, watchlist, total = process_data(data)

        message = create_message(strong, watchlist, total)

        send_telegram(message)

        print("✅ Morning Scanner Completed Successfully")

    except Exception as e:
        send_telegram(f"❌ Morning Scanner Error: {e}")
        print(f"Error: {e}")
