import requests
from datetime import datetime
import os
import time
import json

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
# SAVE CACHE FOR DELAYED POSTS
# ============================
def save_cache(alerts):

    os.makedirs("data", exist_ok=True)

    cache = {
        "alerts": alerts,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("data/last_scanner_cache.json", "w") as f:
        json.dump(cache, f)

    print("✅ Cache file saved")


# ============================
# FETCH NSE PREOPEN
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

        if res.status_code == 200:
            return res.json().get("data", [])

    except Exception as e:
        print(f"NSE fetch error: {e}")

    return []


# ============================
# SMART MONEY ENGINE
# ============================
def get_smart_money_stocks(symbols):

    if not VOLUME_ENABLED:
        return []

    analyzer = VolumeSetupAnalyzer()

    smart_list = []

    try:
        for symbol in symbols[:15]:

            df = fetch_historical_data(
                symbol,
                interval="30minute",
                days=5
            )

            if df is None or len(df) < 25:
                continue

            setups = analyzer.detect_setups(df)

            if not setups:
                continue

            latest = setups[-1]

            range_strength = latest["range"]

            volume_score = min(
                100,
                int(range_strength * 8)
            )

            candle_score = latest["candles"] * 5

            score = min(
                100,
                volume_score + candle_score
            )

            if score >= 45:

                smart_list.append({
                    "symbol": symbol,
                    "score": score,
                    "top": latest["top"],
                    "bottom": latest["bottom"],
                    "candles": latest["candles"],
                    "fab_50": latest.get("fab_50", "N/A")
                })

    except Exception as e:
        print("Smart money error:", e)

    return sorted(
        smart_list,
        key=lambda x: x["score"],
        reverse=True
    )[:7]


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

                strong.append((
                    symbol,
                    change,
                    price
                ))

            elif abs(change) > 0.7:

                watchlist.append((
                    symbol,
                    change,
                    price
                ))

        except:
            continue

    strong = sorted(
        strong,
        key=lambda x: abs(x[1]),
        reverse=True
    )[:5]

    watchlist = sorted(
        watchlist,
        key=lambda x: abs(x[1]),
        reverse=True
    )[:5]

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
# MESSAGE BUILDER
# ============================
def create_message(
    strong,
    watchlist,
    smart,
    total
):

    msg = "📊 *PRE-MARKET INSIGHT (SMART MONEY v2)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"

    bias = get_market_bias(strong)

    msg += f"📊 Market Bias: *{bias}*\n\n"

    if smart:

        msg += "🔥 *SMART MONEY ACCUMULATION*\n"

        for s in smart:

            level = (
                "STRONG"
                if s["score"] >= 70
                else "MODERATE"
            )

            msg += (
                f"• {s['symbol']} | "
                f"Score: {s['score']} | "
                f"{level}\n"
            )

    else:
        msg += "⚠️ No smart money accumulation detected\n"

    if strong:

        msg += "\n🚀 High Momentum Stocks\n"

        for s in strong:

            msg += (
                f"• {s[0]} | "
                f"₹{s[2]} | "
                f"{s[1]:.2f}%\n"
            )

    if watchlist:

        msg += "\n📉 Watchlist\n"

        for s in watchlist:

            msg += (
                f"• {s[0]} | "
                f"₹{s[2]} | "
                f"{s[1]:.2f}%\n"
            )

    msg += "\n⚠️ Educational purpose only"

    msg += (
        f"\n⏰ "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":

    try:

        data = fetch_preopen_data()

        if not data:

            send_telegram(
                "⚠️ No pre-open data received"
            )

            exit()

        strong, watchlist, symbols, total = process_data(data)

      smart = get_smart_money_stocks(symbols)

message = create_message(strong, watchlist, smart, total)

send_telegram(message)

# ============================
# SAVE CACHE FOR DELAYED POSTS
# ============================

import json

alerts = []

for s in smart:

    alerts.append({
        "symbol": s["symbol"],
        "setup": {
            "candles": 3,
            "top": s["top"],
            "bottom": s["bottom"],
            "fab_50": round((s["top"] + s["bottom"]) / 2, 2)
        }
    })

os.makedirs("data", exist_ok=True)

with open("data/last_scanner_cache.json", "w") as f:
    json.dump({"alerts": alerts}, f)

print("✅ Cache file created")

print("✅ Morning Scanner Completed")

    except Exception as e:

        send_telegram(f"❌ Error: {e}")

        print(e)
