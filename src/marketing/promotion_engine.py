import requests
import os
import random
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_MAIN = os.getenv("CHANNEL_FREE_MAIN")
EDUCATION = os.getenv("CHANNEL_EDUCATION")

RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")


def send_message(chat_id, message):
    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True
        }

        response = requests.post(
            url,
            data=payload,
            timeout=20
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


messages = [

f"""
🔥 SMART MONEY SCANNER ACTIVE

Detect:

✅ Breakout Stocks
✅ Volume Blast
✅ Momentum Build-Up
✅ Institutional Buying
✅ Demand Supply Zones

⚠️ Avoid Fake Breakouts & Retail Traps

🎯 Used For Intraday + Swing Trading

🚀 Start Free Trial:
{RAZORPAY_LINK}
""",

f"""
📈 AI MARKET INTELLIGENCE

Premium Includes:

✅ Entry Zones
✅ Momentum Detection
✅ Smart Risk System
✅ Smart Scalping Setups
✅ Institutional Flow Tracking

⚡ Built For Serious Traders

🚀 Join Premium:
{RAZORPAY_LINK}
""",

f"""
🚀 TRADERS ARE SWITCHING TO AI

Why?

✅ Faster Market Detection
✅ Breakout Identification
✅ Momentum Tracking
✅ Smart Risk Management
✅ High Probability Setups

🔥 Upgrade Your Trading System

🎯 Join Now:
{RAZORPAY_LINK}
""",

f"""
🏦 DAILY MARKET EDGE

Premium Members Receive:

✅ Early Breakout Alerts
✅ AI Momentum Detection
✅ Demand Supply Zones
✅ Intraday Trade Ideas
✅ Swing Trade Opportunities

⚡ Trade Smarter With AI

🚀 Upgrade Here:
{RAZORPAY_LINK}
""",

f"""
🔥 INSTITUTIONAL STYLE TRADING

Get Access To:

✅ Smart Money Concepts
✅ AI Breakout Scanner
✅ Volume Expansion Alerts
✅ Momentum Entries
✅ Market Structure Analysis

🎯 Built For Consistent Traders

🚀 Access Premium:
{RAZORPAY_LINK}
"""
]


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
