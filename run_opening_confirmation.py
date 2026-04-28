import requests
import os
from datetime import datetime
import random

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE_CHANNELS = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
]

PREMIUM_CHANNELS = [
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

def send(channels, message):
    for ch in channels:
        if not ch:
            continue
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={
                "chat_id": ch,
                "text": message,
                "parse_mode": "Markdown"
            })
            print(f"✅ Sent to {ch}")
        except Exception as e:
            print(e)

def generate_market_state():
    states = ["BREAKOUT", "RANGE", "WEAK"]
    return random.choice(states)

def free_message(state):
    msg = "⏰ *9:20 MARKET UPDATE*\n\n"

    if state == "BREAKOUT":
        msg += "📊 Market showing breakout attempt\n"
        msg += "👉 Wait for confirmation before entry\n"
    elif state == "WEAK":
        msg += "📊 Market showing weakness\n"
        msg += "👉 Avoid aggressive buying\n"
    else:
        msg += "📊 Market in range\n"
        msg += "👉 No clear direction yet\n"

    msg += "\n⚠️ Informational only"
    return msg

def premium_message(state):
    msg = "⏰ *OPENING CONFIRMATION (9:20)*\n\n"

    if state == "BREAKOUT":
        msg += "📊 Breakout Structure Forming\n"
        msg += "🎯 Trade Above Range → Long\n"
    elif state == "WEAK":
        msg += "📊 Weak Structure\n"
        msg += "🎯 Below Range → Short Bias\n"
    else:
        msg += "📊 Range Formation\n"
        msg += "🎯 Wait for breakout confirmation\n"

    msg += "\n⚡ Rule: No trade without confirmation candle"
    msg += "\n⚠️ For educational use"

    return msg

if __name__ == "__main__":
    state = generate_market_state()

    send(FREE_CHANNELS, free_message(state))
    send(PREMIUM_CHANNELS, premium_message(state))

    print("✅ 9:20 update sent")
