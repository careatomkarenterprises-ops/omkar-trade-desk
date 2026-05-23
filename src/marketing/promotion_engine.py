import requests
import os
import random
from datetime import datetime

# ============================================
# ENV VARIABLES
# ============================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_MAIN = os.getenv("CHANNEL_FREE_MAIN")
EDUCATION = os.getenv("CHANNEL_EDUCATION")

RAZORPAY_LINK = os.getenv("RAZORPAY_LINK")


# ============================================
# TELEGRAM MESSAGE SENDER
# ============================================

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


# ============================================
# PROMOTIONAL MESSAGES
# ============================================

messages = [

f"""
🚨 MOST TRADERS LOSE MONEY

Because They Trade Without Structure

OMKAR TRADE DESK Helps You Detect:

✅ Smart Money Activity
✅ Breakout Before Crowd
✅ Volume Expansion
✅ Institutional Momentum
✅ Trap Avoidance Zones

📊 Daily AI Based Market Intelligence

🎯 Start Your 7 Days Free Trial

⚡ Join Premium:
{RAZORPAY_LINK}
""",

f"""
📈 AI MARKET INTELLIGENCE

Stop Following Random Tips.

Trade With:

✅ Scanner Based Signals
✅ Momentum Stocks
✅ Institutional Logic
✅ Risk Management
✅ Intraday + Swing Analysis

🔥 Built For Serious Traders & Investors

🎯 Free Trial Available

⚡ Upgrade Here:
{RAZORPAY_LINK}
""",

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
🏦 DAILY MARKET EDGE

Premium Members Get:

✅ Equity Analysis
✅ Nifty & BankNifty View
✅ Momentum Detection
✅ Institutional Structure
✅ Smart Risk Levels
✅ High Probability Setups

📊 Designed For Consistent Traders

🔥 Join Premium:
{RAZORPAY_LINK}
""",

f"""
⚡ DON'T TRADE BLINDLY

Most traders enter late.
Professionals enter early.

OMKAR TRADE DESK Provides:

✅ Early Momentum Detection
✅ AI Scanner Alerts
✅ Smart Money Tracking
✅ Institutional Market Structure

🎯 Trade With Logic, Not Emotion

🚀 Join Here:
{RAZORPAY_LINK}
"""
]


# ============================================
# MAIN ENGINE
# ============================================

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

            send_message(
                channel,
                selected
            )

    print("===================================")
    print("✅ PROMOTION ENGINE FINISHED")
    print("===================================")
