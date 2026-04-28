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

📊 Daily AI-Based Market Insights
📈 Intraday Trade Setups
🔥 Pre-Market Intelligence
🎯 Smart Money Scanner
⚡ Momentum Alerts
🏦 Institutional Style Reports

━━━━━━━━━━━━━━━

💰 *Plans*

🥉 Starter → ₹99
🥈 Pro → ₹499
🥇 Elite → ₹1999

━━━━━━━━━━━━━━━

✅ Live Market Updates
✅ High Probability Setups
✅ Learning + Execution
✅ Structured Risk Management

🔗 Join Premium:
{RAZORPAY_LINK}

⏰ {datetime.now().strftime('%H:%M:%S')}

⚠️ Educational purpose only
"""

    return msg


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    print("🚀 Running Promotion Engine")

    message = build_message()

    send_message(message)

    print("✅ Promotion completed")
