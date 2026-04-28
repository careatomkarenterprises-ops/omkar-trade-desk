import os
import requests
from datetime import datetime
import yfinance as yf

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_CHANNELS = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
]

PREMIUM_CHANNELS = [
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

WATCHLIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "BHARTIARTL.NS",
    "ADANIPORTS.NS",
    "ADANIENT.NS"
]


# ============================
# TELEGRAM
# ============================
def send_message(channels, text):

    for ch in channels:

        if not ch:
            continue

        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            payload = {
                "chat_id": ch,
                "text": text,
                "parse_mode": "Markdown"
            }

            requests.post(url, data=payload, timeout=15)

            print(f"✅ Sent to {ch}")

        except Exception as e:
            print("Telegram Error:", e)


# ============================
# FETCH STOCK DATA
# ============================
def fetch_stock(symbol):

    try:
        df = yf.download(
            symbol,
            period="5d",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty or len(df) < 3:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        close = float(latest["Close"])
        prev_close = float(prev["Close"])

        change = ((close - prev_close) / prev_close) * 100

        volume = int(latest["Volume"])

        return {
            "symbol": symbol.replace(".NS", ""),
            "close": round(close, 2),
            "change": round(change, 2),
            "volume": volume
        }

    except Exception as e:
        print(f"❌ Error {symbol}: {e}")
        return None


# ============================
# BUILD SIGNALS
# ============================
def generate_signals():

    signals = []

    for symbol in WATCHLIST:

        data = fetch_stock(symbol)

        if not data:
            continue

        probability = 50

        if data["change"] > 2:
            probability += 25

        if data["volume"] > 10000000:
            probability += 15

        if data["change"] > 4:
            probability += 10

        probability = min(probability, 95)

        if probability >= 70:

            signals.append({
                "symbol": data["symbol"],
                "change": data["change"],
                "close": data["close"],
                "probability": probability
            })

    return sorted(
        signals,
        key=lambda x: x["probability"],
        reverse=True
    )[:5]


# ============================
# FREE MESSAGE
# ============================
def free_message(signals):

    msg = "📊 *END OF DAY MARKET REPORT*\n\n"

    if not signals:
        msg += "⚠️ No high probability setups today\n"

    else:

        msg += "🔥 Strong Closing Stocks:\n\n"

        for s in signals:

            msg += (
                f"• {s['symbol']} "
                f"({s['change']}%)\n"
            )

    msg += "\n🔐 Premium gives exact entry & targets"

    msg += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# PREMIUM MESSAGE
# ============================
def premium_message(signals):

    msg = "🏦 *MULTIBAGGER SCANNER REPORT*\n\n"

    if not signals:

        msg += "⚠️ No institutional setups detected"

    else:

        for s in signals:

            msg += (
                f"🔥 *{s['symbol']}*\n"
                f"📈 Move: {s['change']}%\n"
                f"🎯 Probability: {s['probability']}%\n"
                f"💰 Closing Price: ₹{s['close']}\n\n"
            )

    msg += "📌 Focus on momentum continuation tomorrow\n"

    msg += "\n⚠️ Educational purpose only"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":

    print("🚀 Running Multibagger Scanner")

    signals = generate_signals()

    send_message(FREE_CHANNELS, free_message(signals))

    send_message(PREMIUM_CHANNELS, premium_message(signals))

    print("✅ Scanner Completed")
