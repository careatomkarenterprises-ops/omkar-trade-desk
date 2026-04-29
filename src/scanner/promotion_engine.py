import requests
import os
import random

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")


def send_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, data=payload, timeout=15)

        print("========== TELEGRAM DEBUG ==========")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("CHANNEL:", CHANNEL)
        print("====================================")

        if response.status_code == 200:
            print("✅ Promotion sent successfully")
        else:
            print("❌ Telegram failed")

    except Exception as e:
        print("❌ ERROR:", str(e))


messages = [

f"""🚀 *TRADERS ARE SWITCHING TO PREMIUM*

✅ Live AI Signals
✅ Breakout Scanner
✅ Institutional Logic
✅ Momentum Detection

📈 Learn structured market approach

🔐 Upgrade Now:
{RAZORPAY_LINK}

⚠️ Educational purpose only
""",

f"""📊 *AI MARKET INTELLIGENCE*

Premium Access Includes:

✅ Entry Zones
✅ Smart Risk System
✅ Breakout Detection
✅ Institutional Flow Reading

⚡ Join Premium:
{RAZORPAY_LINK}

⚠️ Educational purpose only
""",

f"""🏦 *INSTITUTIONAL MARKET SCANNER*

📈 Real-time momentum tracking
📉 AI-powered structure analysis

Premium Features:
✅ Early breakout alerts
✅ Market strength detection
✅ Trade planning support

🔐 Access Here:
{RAZORPAY_LINK}

⚠️ Educational purpose only
"""
]


if __name__ == "__main__":

    print("===== STARTING PROMOTION ENGINE =====")

    selected = random.choice(messages)

    send_message(selected)

    print("✅ Daily promotion completed")
