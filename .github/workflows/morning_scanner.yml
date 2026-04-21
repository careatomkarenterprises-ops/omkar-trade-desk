import requests
from datetime import datetime
import os
import time

# NEW IMPORT (SAFE - only used if available)
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
# FETCH NSE PREOPEN DATA
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
# SMART MONEY ENGINE (NEW)
# ============================
def get_smart_money_stocks(symbols):
    """
    Uses 30-min volume structure to detect accumulation
    SAFE: if failure -> returns empty
    """

    if not VOLUME_ENABLED:
        return []

    analyzer = VolumeSetupAnalyzer()
    smart_list = []

    try:
        for symbol in symbols[:10]:  # LIMIT for safety (fast execution)

            df = fetch_historical_data(symbol, interval="30minute", days=5)

            if df is None or len(df) < 20:
                continue

            setups = analyzer.detect_setups(df)

            if not setups:
                continue

            latest = setups[-1]

            # SMART CONDITION
            strength = latest["range"]

            score = min(100, int(strength * 10))

            if score >= 60:
                smart_list.append({
                    "symbol": symbol,
                    "score": score,
                    "top": latest["top"],
                    "bottom": latest["bottom"]
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
# MESSAGE BUILDER (UPDATED)
# ============================
def create_message(strong, watchlist, smart, total):

    msg = "📊 *PRE-MARKET INSIGHT (SMART MONEY)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data Source: NSE Pre-Open + 30m Volume Flow\n"

    bias = get_market_bias(strong)
    msg += f"📊 Market Bias: *{bias}*\n\n"

    # SMART MONEY SECTION (NEW)
    if smart:
        msg += "🔥 *SMART MONEY ACCUMULATION*\n"
        for s in smart:
            level = "STRONG" if s["score"] >= 75 else "MODERATE"
            msg += f"• {s['symbol']} | Score: {s['score']} | {level}\n"
    else:
        msg += "⚠️ No smart money accumulation detected\n"

    # STRONG MOVERS
    if strong:
        msg += "\n🚀 High Momentum Stocks\n"
        for s in strong:
            msg += f"• {s[0]} | ₹{s[2]} | {s[1]:.2f}%\n"
    else:
        msg += "\n⚠️ No strong movers\n"

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
