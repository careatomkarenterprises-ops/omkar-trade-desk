import os
import requests
import yfinance as yf
from datetime import datetime


# =========================================
# TELEGRAM
# =========================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
PREMIUM_CHANNEL = os.getenv("CHANNEL_PREMIUM")
ELITE_CHANNEL = os.getenv("CHANNEL_PREMIUM_ELITE")


# =========================================
# TELEGRAM SEND
# =========================================

def send(msg, channel):

    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        response = requests.post(
            url,
            data={
                "chat_id": channel,
                "text": msg,
                "parse_mode": "Markdown"
            },
            timeout=20
        )

        if response.status_code == 200:
            print(f"✅ Sent to {channel}")
        else:
            print(f"❌ Telegram Error: {response.status_code}")

    except Exception as e:

        print(f"❌ Telegram Exception: {e}")


# =========================================
# FETCH MARKET DATA
# =========================================

def fetch_data():

    try:

        symbols = {

            # GLOBAL INDICES
            "DOW": "^DJI",
            "NASDAQ": "^IXIC",
            "SP500": "^GSPC",

            # INDIA
            "GIFTNIFTY": "^NSEI",

            # COMMODITIES
            "CRUDE": "CL=F",
            "GOLD": "GC=F",
            "SILVER": "SI=F",

            # CURRENCY
            "USDINR": "INR=X",
            "DXY": "DX-Y.NYB"
        }

        data = {}

        for name, ticker in symbols.items():

            ticker_data = yf.Ticker(ticker)

            hist = ticker_data.history(period="2d")

            if len(hist) < 2:
                continue

            prev_close = hist["Close"].iloc[-2]
            latest_close = hist["Close"].iloc[-1]

            change = (
                (latest_close - prev_close)
                / prev_close
            ) * 100

            data[name] = {
                "price": round(latest_close, 2),
                "change": round(change, 2)
            }

        return data

    except Exception as e:

        print(f"❌ Data Fetch Error: {e}")

        return {}


# =========================================
# MARKET ANALYSIS
# =========================================

def analyze_market(data):

    score = 0

    # US MARKETS
    score += data.get("DOW", {}).get("change", 0)
    score += data.get("NASDAQ", {}).get("change", 0)
    score += data.get("SP500", {}).get("change", 0)

    # GIFT NIFTY
    score += data.get("GIFTNIFTY", {}).get("change", 0) * 2

    # FINAL BIAS
    if score > 2:
        bias = "🟢 BULLISH"
    elif score < -2:
        bias = "🔴 BEARISH"
    else:
        bias = "🟡 SIDEWAYS"

    return bias, round(score, 2)


# =========================================
# ESTIMATE NIFTY RANGE
# =========================================

def estimate_range(score):

    nifty_base = 25000

    move = int(score * 120)

    open_price = nifty_base + move

    resistance = open_price + 180
    support = open_price - 180

    return (
        open_price,
        support,
        resistance
    )


# =========================================
# BUILD TELEGRAM MESSAGE
# =========================================

def build_message(data, bias, score):

    open_price, support, resistance = estimate_range(score)

    msg = "📈 *AI PRE-MARKET INTELLIGENCE*\n\n"

    msg += f"🧠 Market Bias: {bias}\n"
    msg += f"⚡ Global Score: {score}\n\n"

    msg += "*🌍 GLOBAL MARKETS*\n"

    for key in ["DOW", "NASDAQ", "SP500"]:

        if key in data:

            msg += (
                f"• {key}: "
                f"{data[key]['change']}%\n"
            )

    msg += "\n*🇮🇳 INDIA OUTLOOK*\n"

    if "GIFTNIFTY" in data:

        msg += (
            f"• GIFT NIFTY: "
            f"{data['GIFTNIFTY']['change']}%\n"
        )

    msg += f"• Expected Open: {open_price}\n"
    msg += f"• Resistance: {resistance}\n"
    msg += f"• Support: {support}\n"

    msg += "\n*🛢 COMMODITIES*\n"

    for key in ["CRUDE", "GOLD", "SILVER"]:

        if key in data:

            msg += (
                f"• {key}: "
                f"{data[key]['change']}%\n"
            )

    msg += "\n*💵 CURRENCY*\n"

    for key in ["USDINR", "DXY"]:

        if key in data:

            msg += (
                f"• {key}: "
                f"{data[key]['change']}%\n"
            )

    msg += "\n⚠️ Educational Purpose Only"

    msg += (
        f"\n⏰ "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    return msg


# =========================================
# MAIN
# =========================================

if __name__ == "__main__":

    print("=======================================")
    print("🚀 RUNNING AI PRE-MARKET ENGINE")
    print("=======================================")

    data = fetch_data()

    if not data:

        send(
            "⚠️ Market data unavailable",
            FREE_CHANNEL
        )

        exit()

    bias, score = analyze_market(data)

    message = build_message(
        data,
        bias,
        score
    )

    # FREE
    send(
        message,
        FREE_CHANNEL
    )

    # PREMIUM
    send(
        message,
        PREMIUM_CHANNEL
    )

    # ELITE
    send(
        message,
        ELITE_CHANNEL
    )

    print("=======================================")
    print("✅ MARKET PREDICTION COMPLETED")
    print("=======================================")
