import os
import requests
from datetime import datetime
import pandas as pd
from kiteconnect import KiteConnect

# =========================================
# ENV VARIABLES
# =========================================

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

# =========================================
# LOAD FNO STOCKS
# =========================================

WATCHLIST = []

try:

    df = pd.read_csv("fno_stocks.csv")

    for stock in df.iloc[:, 0]:

        stock = str(stock).strip().upper()

        if stock and stock != "NAN":

            WATCHLIST.append(stock)

    print(f"✅ Loaded {len(WATCHLIST)} FNO Stocks")

except Exception as e:

    print("❌ CSV LOAD ERROR:", e)

# =========================================
# ZERODHA CONNECTION
# =========================================

kite = None

try:

    kite = KiteConnect(api_key=KITE_API_KEY)

    kite.set_access_token(KITE_ACCESS_TOKEN)

    profile = kite.profile()

    print(f"✅ Zerodha Connected: {profile['user_name']}")

except Exception as e:

    print("❌ Zerodha Connection Failed:", e)
    exit()

# =========================================
# LOAD INSTRUMENT MAP
# =========================================

instrument_map = {}

try:

    instruments = kite.instruments("NSE")

    for item in instruments:

        instrument_map[item["tradingsymbol"]] = item["instrument_token"]

    print(f"✅ Loaded {len(instrument_map)} NSE Instruments")

except Exception as e:

    print("❌ Instrument Load Error:", e)

# =========================================
# TELEGRAM
# =========================================

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

# =========================================
# FETCH STOCK DATA FROM ZERODHA
# =========================================

def fetch_stock(symbol):

    try:

        print(f"📊 Fetching {symbol}")

        if symbol not in instrument_map:

            print(f"⚠️ Instrument Missing: {symbol}")

            return None

        token = instrument_map[symbol]

        data = kite.historical_data(
            instrument_token=token,
            from_date=datetime.now().replace(hour=9, minute=15),
            to_date=datetime.now(),
            interval="day"
        )

        if not data or len(data) < 2:

            print(f"⚠️ No Historical Data: {symbol}")

            return None

        latest = data[-1]
        prev = data[-2]

        close = float(latest["close"])
        prev_close = float(prev["close"])

        change = ((close - prev_close) / prev_close) * 100

        volume = int(latest["volume"])

        return {
            "symbol": symbol,
            "close": round(close, 2),
            "change": round(change, 2),
            "volume": volume
        }

    except Exception as e:

        print(f"❌ Error Fetching {symbol}: {e}")

        return None

# =========================================
# SIGNAL ENGINE
# =========================================

def generate_signals():

    signals = []

    for symbol in WATCHLIST:

        data = fetch_stock(symbol)

        if not data:
            continue

        probability = 50

        # Momentum
        if data["change"] > 2:
            probability += 20

        # Strong breakout
        if data["change"] > 4:
            probability += 20

        # Volume strength
        if data["volume"] > 1000000:
            probability += 15

        # Extreme momentum
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

# =========================================
# FREE MESSAGE
# =========================================

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

# =========================================
# PREMIUM MESSAGE
# =========================================

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

# =========================================
# MAIN
# =========================================

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
