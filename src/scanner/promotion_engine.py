import requests
import os
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")


def send_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHANNEL,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=payload)

    print(response.text)


def build_message():

    return f"""
🚀 *OMKAR TRADE DESK PREMIUM*

📊 AI Market Insights
📈 Intraday Setups
🔥 Momentum Scanner
🎯 Pre-Market Intelligence

━━━━━━━━━━━━━━━

💰 *Plans*

🥉 ₹99 Starter
🥈 ₹499 Pro
🥇 ₹1999 Elite

━━━━━━━━━━━━━━━

🔗 Join Premium:
{RAZORPAY_LINK}

⏰ {datetime.now().strftime('%H:%M:%S')}

⚠️ Educational purpose only
"""


if __name__ == "__main__":

    print("🚀 Running Promotion Engine")

    message = build_message()

    send_message(message)

    print("✅ Promotion completed")
