import requests
import os
import time
from datetime import datetime

from src.scanner.zerodha_fetcher import get_zerodha_fetcher

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
PREMIUM_CHANNEL = os.getenv("CHANNEL_PREMIUM")

# =========================

# TELEGRAM

# =========================

def send(msg, channel):
try:
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

```
    requests.post(url, data={
        "chat_id": channel,
        "text": msg,
        "parse_mode": "Markdown"
    })

except Exception as e:
    print("Telegram Error:", e)
```

# =========================

# STOCK LIST

# =========================

WATCHLIST = [
"RELIANCE",
"HDFCBANK",
"ICICIBANK",
"SBIN",
"TCS",
"INFY",
"AXISBANK",
"ITC",
"LT",
"BAJFINANCE"
]

# =========================

# ANALYZE STOCKS

# =========================

def scan_market():

```
fetcher = get_zerodha_fetcher()

results = []

for symbol in WATCHLIST:

    try:
        df = fetcher.get_stock_data(
            symbol=symbol,
            interval="5minute",
            days=5
        )

        if df is None or len(df) < 10:
            continue

        latest = df.iloc[-1]

        latest_close = latest["close"]
        latest_volume = latest["volume"]

        avg_volume = df["volume"].tail(10).mean()

        volume_ratio = latest_volume / avg_volume

        score = 0

        if volume_ratio > 2:
            score += 40

        if latest_close > df["high"].tail(10).max():
            score += 30

        if latest_close > df["close"].rolling(20).mean().iloc[-1]:
            score += 30

        if score >= 50:

            results.append({
                "symbol": symbol,
                "price": round(latest_close, 2),
                "score": score,
                "volume_ratio": round(volume_ratio, 2)
            })

    except Exception as e:
        print(f"Error scanning {symbol}: {e}")

return sorted(results, key=lambda x: x["score"], reverse=True)
```

# =========================

# MESSAGE

# =========================

def build_messages(results):

```
free_msg = "📊 *PRE-OPEN MOMENTUM STOCKS*\n\n"

for stock in results[:3]:

    free_msg += (
        f"• {stock['symbol']} | "
        f"₹{stock['price']} | "
        f"Score: {stock['score']}\n"
    )

free_msg += "\n🔒 Full breakout analysis in premium"
free_msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

premium_msg = "🔥 *ZERODHA SMART MONEY SCANNER*\n\n"

for stock in results:

    premium_msg += (
        f"• {stock['symbol']}\n"
        f"Price: ₹{stock['price']}\n"
        f"Score: {stock['score']}\n"
        f"Volume Spike: {stock['volume_ratio']}x\n\n"
    )

premium_msg += "📌 High momentum candidates"
premium_msg += "\n⚠️ Educational purpose only"

return free_msg, premium_msg
```

# =========================

# MAIN

# =========================

if **name** == "**main**":

```
print("🚀 Starting Zerodha Scanner...")

results = scan_market()

if not results:

    send("⚠️ No strong setups found today", FREE_CHANNEL)
    exit()

free_msg, premium_msg = build_messages(results)

# PREMIUM FIRST
send(premium_msg, PREMIUM_CHANNEL)

# DELAYED FREE
time.sleep(120)

send(free_msg, FREE_CHANNEL)

print("✅ Scanner Finished")
```
