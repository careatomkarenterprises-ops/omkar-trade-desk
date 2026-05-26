import os
import requests
from datetime import datetime
import pandas as pd
import yfinance as yf
from kiteconnect import KiteConnect

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

FREE_CHANNELS = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
]

PREMIUM_CHANNELS = [
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

WATCHLIST = []

try:

    df = pd.read_csv("fno_stocks.csv")

    for stock in df.iloc[:, 0]:

        stock = str(stock).strip()

        if stock and stock != "nan":

            if not stock.endswith(".NS"):
                stock += ".NS"

            WATCHLIST.append(stock)

    print(f"✅ Loaded {len(WATCHLIST)} Stocks")

except Exception as e:

    print("❌ CSV LOAD ERROR:", e)

kite = None

try:

    if KITE_API_KEY and KITE_ACCESS_TOKEN:

        kite = KiteConnect(api_key=KITE_API_KEY)

        kite.set_access_token(KITE_ACCESS_TOKEN)

        profile = kite.profile()

        print(f"✅ Zerodha Connected: {profile['user_name']}")

    else:

        print("⚠️ Zerodha credentials missing")

except Exception as e:

    print("❌ Zerodha Connection Failed:", e)

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

            response = requests.post(
                url,
                data=payload,
                timeout=20
            )

            print(f"✅ Telegram Sent -> {ch}")

            print(response.text)

        except Exception as e:

            print("❌ Telegram Error:", e)

def fetch_stock(symbol):

    try:

        print(f"📊 Fetching {symbol}")

        df = yf.download(
            symbol,
            period="5d",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty or len(df) < 3:

            print(f"⚠️ No Data: {symbol}")

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

        print(f"❌ Error Fetching {symbol}: {e}")

        return None

def generate_signals():

    signals = []

    for symbol in WATCHLIST:

        data = fetch_stock(symbol)

        if not data:
            continue

        probability = 50

        if data["change"] > 2:
            probability += 20

        if data["change"] > 4:
            probability += 20

        if data["volume"] > 10000000:
            probability += 15

        if data["change"] > 6:
            probability += 10

        probability = min(probability, 95)

        print(
            f"✅ {data['symbol']} | "
            f"Move: {data['change']}% | "
            f"Probability: {probability}%"
        )

        if probability >= 70:

            signals.append({
                "symbol": data["symbol"],
                "change": data["change"],
                "close": data["close"],
                "volume": data["volume"],
                "probability": probability
            })

    return sorted(
        signals,
        key=lambda x: x["probability"],
        reverse=True
    )[:5]

def free_message(signals):

    msg = "📊 *END OF DAY MARKET REPORT*\n\n"

    if not signals:

        msg += "⚠️ No high probability setups today\n"

    else:

        msg += "🔥 Strong Closing Stocks:\n\n"

        for s in signals:

            msg += (
                f"• *{s['symbol']}* "
                f"({s['change']}%)\n"
            )

    msg += "\n🔐 Premium gives exact entry & targets"

    msg += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg

def premium_message(signals):

    msg = "🏦 *MULTIBAGGER SCANNER REPORT*\n\n"

    if not signals:

        msg += "⚠️ No institutional setups detected\n"

    else:

        for s in signals:

            msg += (
                f"🔥 *{s['symbol']}*\n"
                f"📈 Move: {s['change']}%\n"
                f"🎯 Probability: {s['probability']}%\n"
                f"💰 Closing Price: ₹{s['close']}\n"
                f"📊 Volume: {s['volume']}\n\n"
            )

    msg += "📌 Focus on momentum continuation tomorrow\n"

    msg += "\n⚠️ Educational purpose only"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg

if __name__ == "__main__":

    try:

        print("====================================")
        print("🚀 RUNNING MULTIBAGGER SCANNER V2")
        print("====================================")

        signals = generate_signals()

        print(f"✅ Signals Generated: {len(signals)}")

        send_message(
            FREE_CHANNELS,
            free_message(signals)
        )

        send_message(
            PREMIUM_CHANNELS,
            premium_message(signals)
        )

        print("====================================")
        print("✅ SCANNER COMPLETED")
        print("====================================")

    except Exception as e:

        print("❌ MAIN ERROR:", e)
