import requests
import os
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNELS = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

# ============================
# TELEGRAM
# ============================
def send_telegram(message):
    if not BOT_TOKEN:
        print("❌ Missing TELEGRAM_BOT_TOKEN")
        return

    for channel in CHANNELS:
        if not channel:
            continue

        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": channel,
                "text": message,
                "parse_mode": "Markdown"
            }

            res = requests.post(url, data=payload, timeout=10)

            if res.status_code == 200:
                print(f"✅ Sent to {channel}")
            else:
                print(f"❌ Failed: {res.text}")

        except Exception as e:
            print(f"❌ Error: {e}")


# ============================
# NSE DATA (NO LOGIN REQUIRED)
# ============================
def get_nse_data():
    try:
        url = "https://www.nseindia.com/api/marketStatus"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)

        res = session.get(url, headers=headers)
        data = res.json()

        return data

    except Exception as e:
        print("❌ NSE Error:", e)
        return None


# ============================
# SIMPLE LOGIC
# ============================
def analyze_market():
    data = get_nse_data()

    if not data:
        return None

    try:
        market_status = data["marketState"][0]["marketStatus"]

        if market_status == "Open":
            sentiment = "LIVE MARKET"
        else:
            sentiment = "PRE-MARKET"

        return sentiment

    except:
        return "NEUTRAL"


# ============================
# MESSAGE
# ============================
def create_message():
    sentiment = analyze_market()

    if not sentiment:
        return "⚠️ Market data unavailable. Stay cautious today."

    msg = "🌅 *PRE-MARKET MARKET INTELLIGENCE*\n\n"

    msg += f"📊 Market Phase: *{sentiment}*\n\n"

    msg += "📌 Today's Approach:\n"
    msg += "• Wait for first 15 mins confirmation\n"
    msg += "• Avoid early breakout traps\n"
    msg += "• Focus on high volume stocks\n\n"

    msg += "⚡ Strategy:\n"
    msg += "• Trade only after structure confirmation\n"
    msg += "• Avoid overtrading\n\n"

    msg += f"⏰ {datetime.now().strftime('%H:%M:%S')}\n"
    msg += "\n⚠️ Informational only. No buy/sell recommendation."

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    try:
        print("🚀 Running Stable Market Predictor...")

        message = create_message()

        print("📩 Message:")
        print(message)

        send_telegram(message)

        print("✅ Done")

    except Exception as e:
        print("❌ Error:", e)
