import requests
import os
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")
RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")


# =========================
# TELEGRAM SEND
# =========================
def send_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown"
        }

        requests.post(url, data=payload, timeout=10)

        print("✅ Promotion sent")

    except Exception as e:
        print("Telegram Error:", e)


# =========================
# PROMOTION MESSAGE
# =========================
def build_message():

    msg = f"""
🚀 *OMKAR TRADE DESK PREMIUM*

✅ Daily AI-Based Market Analysis
✅ Pre-Market Probability Scanner
✅ Intraday Momentum Scanner
✅ Smart Money Tracking
✅ Opening Confirmation System
✅ Premium Trade Levels
✅ Risk Management Updates

📈 Upgrade Your Trading Experience Today

🔥 *Plans Starting From ₹99*

💳 Join Now:
{RAZORPAY_LINK}

⏰ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}

⚠️ Educational Purpose Only
"""

    return msg


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    print("🚀 Running Promotion Engine")

    message = build_message()

    send_message(message)

    print("✅ Done")
