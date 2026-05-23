```python
import os
import json
import time
import requests
import pandas as pd

from datetime import datetime

from src.zerodha_fetcher import get_zerodha_fetcher


# =====================================================
# ENV VARIABLES
# =====================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
PREMIUM_CHANNEL = os.getenv("CHANNEL_PREMIUM")
ELITE_CHANNEL = os.getenv("CHANNEL_PREMIUM_ELITE")


# =====================================================
# TELEGRAM
# =====================================================

def send_telegram(message, channel):

    if not channel:
        return

    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": channel,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(
            url,
            data=payload,
            timeout=20
        )

        if response.status_code == 200:
            print(f"✅ Telegram Sent -> {channel}")

        else:
            print(f"❌ Telegram Error -> {response.status_code}")

    except Exception as e:

        print(f"❌ Telegram Exception -> {e}")


# =====================================================
# STOCK LIST
# =====================================================

WATCHLIST = [

    "RELIANCE",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "INFY",
    "TCS",
    "LT",
    "AXISBANK",
    "KOTAKBANK",
    "BHARTIARTL",
    "ITC",
    "TATAMOTORS",
    "MARUTI",
    "SUNPHARMA",
    "BAJFINANCE"

]


# =====================================================
# VOLUME ANALYSIS
# =====================================================

def analyze_stock(symbol, fetcher):

    try:

        df = fetcher.get_historical_data(
            symbol,
            interval="30minute",
            days=10
        )

        if df is None:
            return None

        if len(df) < 20:
            return None

        latest = df.iloc[-1]

        avg_volume = df["volume"].tail(10).mean()

        latest_volume = latest["volume"]

        volume_ratio = latest_volume / avg_volume

        price_change = (
            (latest["close"] - latest["open"])
            / latest["open"]
        ) * 100

        score = 0

        # =================================================
        # VOLUME EXPANSION
        # =================================================

        if volume_ratio > 2:
            score += 40

        elif volume_ratio > 1.5:
            score += 25

        # =================================================
        # MOMENTUM
        # =================================================

        if abs(price_change) > 1:
            score += 30

        elif abs(price_change) > 0.5:
            score += 15

        # =================================================
        # TREND STRENGTH
        # =================================================

        ema20 = df["close"].ewm(span=20).mean().iloc[-1]

        if latest["close"] > ema20:
            score += 20

        # =================================================
        # RANGE BREAK
        # =================================================

        recent_high = df["high"].tail(15).max()

        if latest["close"] >= recent_high:
            score += 20

        direction = "BULLISH"

        if price_change < 0:
            direction = "BEARISH"

        return {
            "symbol": symbol,
            "price": round(latest["close"], 2),
            "change": round(price_change, 2),
            "volume_ratio": round(volume_ratio, 2),
            "score": score,
            "direction": direction
        }

    except Exception as e:

        print(f"❌ Analysis Error ({symbol}) -> {e}")

        return None


# =====================================================
# SCANNER ENGINE
# =====================================================

def run_scanner():

    fetcher = get_zerodha_fetcher()

    results = []

    for symbol in WATCHLIST:

        print(f"🔍 Scanning {symbol}")

        stock = analyze_stock(symbol, fetcher)

        if stock:

            if stock["score"] >= 40:
                results.append(stock)

        time.sleep(0.5)

    return sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )


# =====================================================
# MARKET BIAS
# =====================================================

def get_market_bias(results):

    bullish = len([
        x for x in results
        if x["direction"] == "BULLISH"
    ])

    bearish = len([
        x for x in results
        if x["direction"] == "BEARISH"
    ])

    if bullish > bearish:
        return "🟢 BULLISH"

    elif bearish > bullish:
        return "🔴 BEARISH"

    return "🟡 SIDEWAYS"


# =====================================================
# MESSAGE BUILDER
# =====================================================

def build_messages(results):

    bias = get_market_bias(results)

    # =================================================
    # FREE MESSAGE
    # =================================================

    free_msg = "📊 *SMART MONEY MARKET SCANNER*\n\n"

    free_msg += f"🧠 Market Bias: {bias}\n\n"

    if results:

        free_msg += "🔥 Momentum Stocks:\n\n"

        for r in results[:3]:

            free_msg += (
                f"• {r['symbol']} | "
                f"{r['change']}%\n"
            )

    else:

        free_msg += "⚠️ No strong setups detected"

    free_msg += "\n\n🔒 Premium gives exact levels"

    free_msg += (
        f"\n⏰ "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    # =================================================
    # PREMIUM MESSAGE
    # =================================================

    premium_msg = "🏦 *INSTITUTIONAL FLOW SCANNER*\n\n"

    premium_msg += f"📊 Market Bias: {bias}\n\n"

    if results:

        for r in results:

            premium_msg += (
                f"• {r['symbol']} | "
                f"₹{r['price']} | "
                f"{r['change']}% | "
                f"Vol x{r['volume_ratio']} | "
                f"Score: {r['score']} | "
                f"{r['direction']}\n"
            )

    else:

        premium_msg += "⚠️ No institutional setups detected"

    premium_msg += "\n📌 Trade only after confirmation"

    premium_msg += "\n⚠️ Educational Purpose Only"

    premium_msg += (
        f"\n⏰ "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    return free_msg, premium_msg


# =====================================================
# CACHE
# =====================================================

def save_cache(results):

    try:

        os.makedirs("data", exist_ok=True)

        with open(
            "data/last_scanner_cache.json",
            "w"
        ) as f:

            json.dump(results, f)

        print("✅ Scanner Cache Saved")

    except Exception as e:

        print(f"❌ Cache Error -> {e}")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print("=======================================")
    print("🚀 STARTING SMART MONEY SCANNER")
    print("=======================================")

    results = run_scanner()

    if not results:

        send_telegram(
            "⚠️ No strong setups detected today",
            FREE_CHANNEL
        )

        exit()

    free_msg, premium_msg = build_messages(results)

    print("📤 Sending Free Alert")

    send_telegram(
        free_msg,
        FREE_CHANNEL
    )

    print("📤 Sending Premium Alert")

    send_telegram(
        premium_msg,
        PREMIUM_CHANNEL
    )

    print("📤 Sending Elite Alert")

    send_telegram(
        premium_msg,
        ELITE_CHANNEL
    )

    save_cache(results)

    print("=======================================")
    print("✅ SMART MONEY SCANNER COMPLETED")
    print("=======================================")
```
