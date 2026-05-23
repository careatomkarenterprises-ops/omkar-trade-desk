import requests
import os
import random
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_MAIN = os.getenv("CHANNEL_FREE_MAIN")
EDUCATION = os.getenv("CHANNEL_EDUCATION")

RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")


# =========================================
# TELEGRAM SEND
# =========================================
def send_message(chat_id, message):

    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message
        }

        response = requests.post(
            url,
            data=payload,
            timeout=15
        )

        print("===================================")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code == 200:
            print(f"✅ Message sent to {chat_id}")
        else:
            print(f"❌ Failed for {chat_id}")

    except Exception as e:

        print("❌ ERROR:", str(e))


# =========================================
# MARKETING MESSAGES
# =========================================
messages = [

f"""
🚀 OMKAR TRADE DESK PREMIUM

AI Based Market Intelligence

✅ Intraday Trade Setups
✅ Breakout Scanner
✅ Smart Money Tracking
✅ Momentum Detection
✅ Risk Management Levels
✅ Daily Market Analysis
✅ Educational Content

🎯 Plans Starting From ₹999

⚡ Start Free Trial:
{RAZORPAY_LINK}
""",

f"""
📈 AI MARKET INTELLIGENCE

Premium Includes:

✅ Entry Zones
✅ Momentum Detection
✅ Smart Risk System
✅ Institutional Logic
✅ Daily Market View

🔥 Built For Serious Traders

⚡ Join Now:
{RAZORPAY_LINK}
""",

f"""
🏦 DAILY MARKET EDGE

Premium Members Receive:

✅ Early Breakout Alerts
✅ AI Momentum Detection
✅ Smart Risk Management
✅ Equity & Index Analysis
✅ Institutional Market View

🎯 Free Trial Available

🔥 Upgrade Here:
{RAZORPAY_LINK}
""",

f"""
📊 TRADE WITH STRUCTURE

Most traders follow emotions.
Professionals follow systems.

OMKAR TRADE DESK Gives:

✅ Scanner Based Setups
✅ Momentum Stocks
✅ Institutional Concepts
✅ Smart Risk Management

🚀 Join Premium:
{RAZORPAY_LINK}
""",

f"""
🔥 SMART MONEY SCANNER

Detect:

✅ Volume Expansion
✅ Breakout Stocks
✅ Momentum Build-Up
✅ Institutional Activity

🎯 Designed For Traders & Investors

⚡ Join:
{RAZORPAY_LINK}
"""
]


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    print("===================================")
    print("🚀 STARTING PROMOTION ENGINE")
    print(datetime.now())
    print("===================================")

    selected = random.choice(messages)

    channels = [
        FREE_MAIN,
        EDUCATION
    ]

    for channel in channels:

        if channel:
            send_message(channel, selected)

    print("===================================")
    print("✅ PROMOTION ENGINE FINISHED")
    print("===================================")
