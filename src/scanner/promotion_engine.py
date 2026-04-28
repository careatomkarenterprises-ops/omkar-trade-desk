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

        requests.post(url, data=payload, timeout=10)

        print("✅ Promotion sent successfully")

    except Exception as e:
        print("❌ Telegram Error:", e)


messages = [
    f"""🚀 *TRADERS ARE SWITCHING TO PREMIUM*

✅ Live AI Signals
✅ Probability-Based Trades
✅ Institutional Trade Logic
✅ High Momentum Scanner

🔥 Upgrade Now:
{RAZORPAY_LINK}
""",

    f"""📈 *TODAY'S MARKET MOVES WERE CAPTURED EARLY*

Premium Members Received:
✅ Early Entry Zones
✅ Breakout Alerts
✅ Smart Risk Management

🔐 Join Premium:
{RAZORPAY_LINK}
""",

    f"""🏦 *AI-POWERED MARKET INTELLIGENCE*

Our Premium System Includes:
✅ Pre-Market Prediction
✅ Smart Opening Confirmation
✅ Momentum Scanner
✅ Probability Scores

⚡ Upgrade Today:
{RAZORPAY_LINK}
"""
]


if __name__ == "__main__":
    selected = random.choice(messages)

    send_message(selected)

    print("✅ Daily promotion completed")
