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
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
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
# MARKETING CONTENT
# =========================================
messages = [

    f"""
🚨 *MOST RETAIL TRADERS LOSE MONEY*

Why?

❌ Late Entry
❌ No Proper Setup
❌ Emotional Trading
❌ Fake Breakouts

Omkar Trade Desk Helps With:

✅ AI Market Scanner
✅ Momentum Detection
✅ Smart Money Logic
✅ Risk Management
✅ Institutional Style Analysis

🔥 Start 7 Days Free Trial

🔐 Upgrade Here:
{RAZORPAY_LINK}

⚠️ Educational Purpose Only
""",

    f"""
📈 *AI MARKET INTELLIGENCE*

Premium Includes:

✅ Entry Zones
✅ Momentum Detection
✅ Smart Risk System
✅ Intraday Trading Setups
✅ Swing Trade Analysis
✅ Market Direction Alerts

🎯 Built For Serious Traders

🔥 7 Days Free Access

⚡ Join Now:
{RAZORPAY_LINK}

⚠️ Educational Purpose Only
""",

    f"""
🏦 *DAILY MARKET EDGE*

Premium Members Receive:

✅ Early Breakout Alerts
✅ AI Momentum Detection
✅ Smart Risk Management
✅ Intraday & Swing Calls
✅ Institutional Market Logic

📊 Equity • Index • Commodity • Currency

🔥 Free Trial Available

🚀 Upgrade Here:
{RAZORPAY_LINK}

⚠️ Educational Purpose Only
""",

    f"""
🔥 *SMART MONEY TRADING SYSTEM*

What You Get:

✅ High Probability Setups
✅ Live Market Analysis
✅ Smart Entry Zones
✅ Demand & Supply Logic
✅ Advanced Scanner Signals

📈 Perfect For:
• Intraday Traders
• Swing Traders
• Positional Traders

🎁 7 Days Free Trial

🔐 Join Premium:
{RAZORPAY_LINK}

⚠️ Educational Purpose Only
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
