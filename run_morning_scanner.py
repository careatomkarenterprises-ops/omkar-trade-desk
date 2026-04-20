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

    # Important: Load homepage first (cookie setup)
    session.get("https://www.nseindia.com", headers=headers)
    time.sleep(1)

    for _ in range(3):
        try:
            res = session.get(url, headers=headers, timeout=10)

            if res.status_code == 200:
                return res.json().get("data", [])

            time.sleep(2)

        except:
            time.sleep(2)

    return []


# ============================
# TRADE LOGIC (ENTRY/SL/TARGET)
# ============================
def generate_trade(symbol, change, price):
    try:
        if change > 0:
            # Bullish
            entry = price * 1.002
            sl = price * 0.995
            target = price * 1.015
            side = "BUY"
            confidence = min(90, abs(change) * 10)

        else:
            # Bearish
            entry = price * 0.998
            sl = price * 1.005
            target = price * 0.985
            side = "SELL"
            confidence = min(90, abs(change) * 10)

        return {
            "symbol": symbol,
            "side": side,
            "entry": round(entry, 2),
            "sl": round(sl, 2),
            "target": round(target, 2),
            "change": round(change, 2),
            "confidence": int(confidence)
        }

    except:
        return None


# ============================
# PROCESS DATA (FILTERED)
# ============================
def process_data(data):
    trades = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            # ✅ FILTERS (VERY IMPORTANT)
            if (
                price > 100 and
                abs(change) > 1.5 and
                symbol.isalpha()
            ):
                trade = generate_trade(symbol, change, price)
                if trade:
                    trades.append(trade)

        except:
            continue

    # Sort strongest first
    trades = sorted(trades, key=lambda x: abs(x["change"]), reverse=True)

    return trades[:8]


# ============================
# FORMAT MESSAGE
# ============================
def create_message(trades):
    msg = "📊 *PRE-MARKET TRADE SIGNALS (NSE)*\n\n"

    if not trades:
        return "⚠️ No strong setups found today."

    for t in trades:
        msg += (
            f"🔹 *{t['symbol']}* ({t['side']})\n"
            f"Entry: ₹{t['entry']}\n"
            f"SL: ₹{t['sl']}\n"
            f"Target: ₹{t['target']}\n"
            f"Move: {t['change']}%\n"
            f"Confidence: {t['confidence']}%\n\n"
        )

    msg += "⚠️ *Wait for confirmation after 9:20 AM*\n"
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN RUN
# ============================
if __name__ == "__main__":
    try:
        data = fetch_preopen_data()

        if not data:
            raise Exception("No data from NSE")

        trades = process_data(data)

        message = create_message(trades)

        send_telegram(message)

        print("✅ Signals sent successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
