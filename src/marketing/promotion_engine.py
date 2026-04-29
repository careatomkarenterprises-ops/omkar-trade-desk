import requests
import os
import random

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")

print("===== TELEGRAM DEBUG =====")
print("BOT TOKEN EXISTS:", bool(BOT_TOKEN))
print("CHANNEL:", CHANNEL)
print("RAZORPAY LINK EXISTS:", bool(RAZORPAY_LINK))


def send_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(
            url,
            data=payload,
            timeout=15
        )

        print("STATUS CODE:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code == 200:
            print("✅ Promotion sent successfully")
        else:
            print("❌ Telegram API failed")

    except Exception as e:
        print("❌ Telegram Error:", str(e))


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
    print("===== STARTING PROMOTION ENGINE =====")

    selected = random.choice(messages)

    send_message(selected)

    print("===== SCRIPT FINISHED =====")
