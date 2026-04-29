import requests
import os
import random

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_MAIN = os.getenv("CHANNEL_FREE_MAIN")
EDUCATION = os.getenv("CHANNEL_EDUCATION")

RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")


def send_message(chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message
        }

        response = requests.post(url, data=payload, timeout=15)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code == 200:
            print(f"✅ Message sent to {chat_id}")
        else:
            print(f"❌ Failed for {chat_id}")

    except Exception as e:
        print("❌ ERROR:", str(e))


messages = [
    f"""🚀 TRADERS ARE SWITCHING TO PREMIUM

✅ Live AI Signals
✅ Breakout Scanner
✅ Institutional Logic

🔐 Upgrade:
{RAZORPAY_LINK}
""",

    f"""📈 AI MARKET INTELLIGENCE

Premium Includes:
✅ Entry Zones
✅ Momentum Detection
✅ Smart Risk System

⚡ Join:
{RAZORPAY_LINK}
""",

    f"""🏦 DAILY MARKET EDGE

Premium Members Receive:
✅ Early Breakout Alerts
✅ AI Momentum Detection
✅ Smart Risk Management

🔥 Upgrade:
{RAZORPAY_LINK}
"""
]


if __name__ == "__main__":

    print("===== STARTING PROMOTION ENGINE =====")

    selected = random.choice(messages)

    channels = [
        FREE_MAIN,
        EDUCATION
    ]

    for channel in channels:
        if channel:
            send_message(channel, selected)

    print("===== SCRIPT FINISHED =====")
