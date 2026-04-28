import requests
import os
import random
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

        requests.post(url, data=payload, timeout=15)

        print("✅ Promotion message sent")

    except Exception as e:
        print("❌ Telegram Error:", e)


# =========================
# PROMOTION MESSAGES
# =========================
PROMOS = [

"""🔥 *TRADERS NOTICE*

Most traders lose because they trade without structure.

📊 Our AI system tracks:
✅ Breakouts
✅ Momentum
✅ Intraday setups
✅ Pre-market sentiment

🎯 Learn structured trading approach.

🔐 Premium Access:
₹99 → Trial
₹499 → Swing Access
₹1999 → Elite Access

👇 Join Here
{link}

⚠️ Educational purpose only
""",

"""🚀 *AI SCANNER ALERT SYSTEM*

Our automated system tracks:

✅ Breakout stocks
✅ Intraday momentum
✅ BankNifty direction
✅ High probability setups

📈 Built for serious learners.

🎯 Upgrade Your Access:
₹99 Starter
₹499 Pro
₹1999 Elite

👇 Join Premium
{link}

⚠️ Informational only
""",

"""🏦 *MARKET EDGE SYSTEM*

Retail traders react late.

Our system monitors:
⚡ Momentum
⚡ Volume
⚡ Breakouts
⚡ Trend continuation

📊 Real-time structured updates.

🔐 Upgrade Access:
₹99 Trial
₹499 Advanced
₹1999 Elite

👇 Access Here
{link}

⚠️ Educational only
"""
]


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    selected = random.choice(PROMOS)

    msg = selected.format(link=RAZORPAY_LINK)

    send_message(msg)

    print("✅ Promotion engine completed")
