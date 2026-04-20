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

    # Load homepage to get cookies
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
# PROCESS DATA (CLEAN + SAFE)
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

            # Basic filters
            if not symbol.isalpha() or price <= 0:
                continue

            # Strong movers
            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            # Medium movers
            elif abs(change) > 0.7:
                watchlist.append((symbol, change, price))

        except:
            continue

    strong = sorted(strong, key=lambda x: abs(x[1]), reverse=True)[:5]
    watchlist = sorted(watchlist, key=lambda x: abs(x[1]), reverse=True)[:5]

    return strong, watchlist, len(data)


# ============================
# MARKET INSIGHT LOGIC
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
# FORMAT MESSAGE (COMPLIANT)
# ============================
def create_message(strong, watchlist, total):
    msg = "📊 *PRE-MARKET MARKET INSIGHT (NSE)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data Source: NSE Pre-Open Market\n"

    bias = get_market_bias(strong)
    msg += f"📊 Market Bias: *{bias}*\n\n"

    # Strong movers
    if strong:
        msg += "🚀 *High Momentum Stocks*\n"
        for s in strong:
            direction = "Positive" if s[1] > 0 else "Negative"
            msg += f"• {s[0]} | ₹{s[2]} | {direction} move ({s[1]:.2f}%)\n"
    else:
        msg += "⚠️ No high momentum stocks in pre-market\n"

    # Watchlist
    if watchlist:
        msg += "\n📉 *Early Watchlist (Moderate Activity)*\n"
        for s in watchlist:
            direction = "Positive" if s[1] > 0 else "Negative"
            msg += f"• {s[0]} | ₹{s[2]} | {direction} ({s[1]:.2f}%)\n"

    # Insight
    msg += "\n\n🧠 *Market Insight*\n"
    if not strong:
        msg += "Low volatility detected. Avoid aggressive trades.\n"
    else:
        msg += "Momentum observed in select stocks. Watch for confirmation after market open.\n"

    # Compliance-safe guidance
    msg += "\n⚠️ *For educational & research purposes only.*\n"
    msg += "Not a buy/sell recommendation.\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        data = fetch_preopen_data()

        if not data:
            raise Exception("No data received from NSE")

        strong, watchlist, total = process_data(data)

        message = create_message(strong, watchlist, total)

        send_telegram(message)

        print("✅ Pre-market insight sent successfully")

    except Exception as e:
        print(f"❌ Error: {e}")