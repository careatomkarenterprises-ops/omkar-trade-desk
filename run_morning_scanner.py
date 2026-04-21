import requests
from datetime import datetime
import os
import time
import yfinance as yf
from src.scanner.volume_analyzer import VolumeSetupAnalyzer

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")

analyzer = VolumeSetupAnalyzer()


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

    except:
        pass

    return []


# ============================
# 30 MIN SMART MONEY CHECK
# ============================
def get_smart_money_signal(symbol):
    try:
        yf_symbol = symbol + ".NS"

        df = yf.download(yf_symbol, interval="30m", period="5d", progress=False)

        if df is None or df.empty:
            return None

        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }).dropna()

        setups = analyzer.detect_setups(df)

        if not setups:
            return None

        latest = setups[-1]

        return {
            "top": latest["top"],
            "bottom": latest["bottom"],
            "range": latest["range"],
            "fab_50": latest["fab_50"]
        }

    except:
        return None


# ============================
# PROCESS DATA
# ============================
def process_data(data):
    strong = []
    watchlist = []
    smart_money = []

    for item in data:
        try:
            meta = item["metadata"]

            symbol = meta.get("symbol", "")
            price = meta.get("iep", 0)
            change = meta.get("pChange", 0)

            if not symbol or price <= 0:
                continue

            # normal movers
            if price > 100 and abs(change) > 1.5:
                strong.append((symbol, change, price))

            elif abs(change) > 0.7:
                watchlist.append((symbol, change, price))

            # SMART MONEY LAYER
            sm = get_smart_money_signal(symbol)
            if sm:
                smart_money.append((symbol, sm))

        except:
            continue

    strong = sorted(strong, key=lambda x: abs(x[1]), reverse=True)[:5]
    watchlist = sorted(watchlist, key=lambda x: abs(x[1]), reverse=True)[:5]
    smart_money = smart_money[:5]

    return strong, watchlist, smart_money, len(data)


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
# MESSAGE BUILDER (UPGRADED)
# ============================
def create_message(strong, watchlist, smart_money, total):

    msg = "📊 *PRE-MARKET INSIGHT (SMART MONEY)*\n\n"

    msg += f"📡 Stocks Scanned: {total}\n"
    msg += f"📍 Data Source: NSE Pre-Open + 30m Volume Flow\n"

    bias = get_market_bias(strong)
    msg += f"📊 Market Bias: *{bias}*\n\n"

    # SMART MONEY SECTION 🔥
    if smart_money:
        msg += "🔥 *SMART MONEY SETUPS (INSTITUTIONAL FLOW)*\n"
        for s, sm in smart_money:
            msg += f"• {s}\n"
            msg += f"  Range: {sm['bottom']} - {sm['top']}\n"
            msg += f"  Zone: {sm['fab_50']}\n\n"
    else:
        msg += "⚠️ No smart money accumulation detected\n\n"

    # Strong movers
    if strong:
        msg += "🚀 *High Momentum Stocks*\n"
        for s in strong:
            direction = "Positive" if s[1] > 0 else "Negative"
            msg += f"• {s[0]} | ₹{s[2]} | {direction} ({s[1]:.2f}%)\n"
    else:
        msg += "⚠️ No strong movers\n"

    # Watchlist
    if watchlist:
        msg += "\n📉 *Watchlist*\n"
        for s in watchlist:
            direction = "Positive" if s[1] > 0 else "Negative"
            msg += f"• {s[0]} | ₹{s[2]} | {direction} ({s[1]:.2f}%)\n"

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

        strong, watchlist, smart_money, total = process_data(data)

        message = create_message(strong, watchlist, smart_money, total)

        send_telegram(message)

        print("✅ Morning Scanner Completed")

    except Exception as e:
        send_telegram(f"❌ Error: {e}")
        print(e)
