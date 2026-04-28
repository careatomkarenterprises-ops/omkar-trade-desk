import requests
import os
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNEL = os.getenv("CHANNEL_FREE_MAIN")

RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")


# ============================
# TELEGRAM
# ============================
def send_message(message):

    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "Markdown"
        }

        requests.post(url, data=payload, timeout=10)

        print("✅ Promotion Sent")

    except Exception as e:

        print("Telegram Error:", e)


# ============================
# PROMOTION MESSAGE
# ============================
def create_message():

    msg = "🚀 *OMKAR TRADE DESK PREMIUM*\n\n"

    msg += "📊 What You Get:\n"
    msg += "• Pre-market intelligence\n"
    msg += "• Intraday momentum alerts\n"
    msg += "• Smart money setups\n"
    msg += "• 9:20 confirmation strategy\n"
    msg += "• Multibagger stock scanner\n\n"

    msg += "🎯 Membership Plans:\n"
    msg += "• Starter → ₹99\n"
    msg += "• Pro → ₹499\n"
    msg += "• Elite → ₹1999\n\n"

    msg += "⚡ Upgrade Your Trading System Today\n\n"

    if RAZORPAY_LINK:
        msg += f"💳 Join Now:\n{RAZORPAY_LINK}\n\n"

    msg += "📌 Educational purpose only"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":

    print("🚀 Running Promotion Engine")

    message = create_message()

    send_message(message)

    print("✅ Promotion Completed")
