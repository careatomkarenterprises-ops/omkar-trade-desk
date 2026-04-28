import requests
import os
from datetime import datetime

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

        response = requests.post(url, data=payload, timeout=10)

        print(response.text)

    except Exception as e:
        print("Telegram Error:", e)


def build_message():

    return f"""
🚀 *OMKAR TRADE DESK PREMIUM*

📊 AI-Based Market Insights
📈 Intraday Setups
🔥 Pre-Market Intelligence
🎯 Momentum Scanner

━━━━━━━━━━━━━━━

💰 *Plans*

🥉 ₹99 Starter
🥈 ₹499 Pro
🥇 ₹1999 Elite

━━━━━━━━━━━━━━━

🔗 Join Now:
{RAZORPAY_LINK}

⏰ {datetime.now().strftime('%H:%M:%S')}

⚠️ Educational purpose only
"""


if __name__ == "__main__":

    print("🚀 Running Promotion Engine")

    msg = build_message()

    send_message(msg)

    print("✅ Promotion completed")
