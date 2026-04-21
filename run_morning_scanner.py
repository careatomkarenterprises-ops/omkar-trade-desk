import requests
from datetime import datetime
import os
import time

# NEW IMPORT (SAFE)
try:
    from src.scanner.volume_analyzer import VolumeSetupAnalyzer
    from src.scanner.data_fetcher import fetch_historical_data
    VOLUME_ENABLED = True
except:
    VOLUME_ENABLED = False


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
# NSE PREOPEN DATA
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
        print(f"NSE fetch error: {e}")

    return []


# ============================
# SMART MONEY ENGINE (FIXED)
# ============================
def get_smart_money_stocks(symbols):

    if not VOLUME_ENABLED:
        return []

    analyzer = VolumeSetupAnalyzer()
    smart_list = []

    try:
        for symbol in symbols[:8]:  # safe limit

            df = fetch_historical_data(symbol, interval="15minute", days=5)

            if df is None or len(df) < 30:
                continue

            setups = analyzer.detect_setups(df)

            if not setups:
                continue

            latest = setups[-1]

            # 🔥 REAL SMART MONEY SCORE (volume + range combined)
            volume_strength = latest["candles"]
            price_range = latest["range"]

            score = min(100, int((volume_strength * 8) + (price_range / 10)))

            if score >= 65:
                smart_list.append({
                    "symbol": symbol,
                    "score": score
                })

    except Exception as e:
        print("Smart money error:", e)

    return sorted(smart_list, key=lambda x: x["score"], reverse=True)[:5]


# ============================
# PROCESS DATA
# ============================
def process_data(data):

    strong = []
    watchlist = []
    symbols = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            if not symbol or price <= 0:
                continue

            symbols.append(symbol)

            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            elif abs(change) > 0.7:
                watchlist.append((symbol, change, price))

        except:
            continue

    strong = sorted(strong, key=lambda x: abs(x[1]), reverse=True)[:5]
    watchlist = sorted(watchlist, key=lambda x: abs(x[1]), reverse=True)[:5]

    return strong, watchlist, symbols, len(data)


# ============================
# MESSAGE BUILDER
# ============================
def create_message(strong, watchlist, smart, total):

    msg = "📊 *PRE-MARKET INSIGHT (SMART MONEY)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data Source: NSE Pre-Open + Volume Flow\n"

    # SMART MONEY
    if smart:
        msg += "\n🔥 *SMART MONEY ACCUMULATION*\n"
        for s in smart:
            level = "STRONG" if s["score"] >= 75 else "MODERATE"
            msg += f"• {s['symbol']} | Score: {s['score']} | {level}\n"
    else:
        msg += "\n⚠️ No smart money accumulation detected\n"

    # MOVERS
    if strong:
        msg += "\n🚀 High Momentum Stocks\n"
        for s in strong:
            msg += f"• {s[0]} | ₹{s[2]} | {s[1]:.2f}%\n"

    # WATCHLIST
    if watchlist:
        msg += "\n📉 Watchlist\n"
        for s in watchlist:
            msg += f"• {s[0]} | ₹{s[2]} | {s[1]:.2f}%\n"

    msg += "\n⚠️ Educational purpose only"
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        data = fetch_preopen_data()

        if not data:
            send_telegram("⚠️ No pre-open data received")
            exit()

        strong, watchlist, symbols, total = process_data(data)

        smart = get_smart_money_stocks(symbols)

        message = create_message(strong, watchlist, smart, total)

        send_telegram(message)

        print("✅ Morning Scanner Completed")

    except Exception as e:
        send_telegram(f"❌ Error: {e}")
        print(e)
