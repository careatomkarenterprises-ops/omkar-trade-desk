import requests
import os
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

FREE = [
    os.getenv("CHANNEL_FREE_MAIN"),
    os.getenv("CHANNEL_FREE_SIGNALS"),
]

PREMIUM = [
    os.getenv("CHANNEL_PREMIUM"),
    os.getenv("CHANNEL_PREMIUM_ELITE"),
]

def send(channels, msg):
    for ch in channels:
        if not ch:
            continue
        try:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
                "chat_id": ch,
                "text": msg,
                "parse_mode": "Markdown"
            })
        except:
            pass


def free_msg():
    return f"""⏰ *9:20 MARKET UPDATE*

📊 Market forming structure
👉 Wait for confirmation

🔐 Premium = Exact trade trigger

⏰ {datetime.now().strftime('%H:%M:%S')}
"""


def premium_msg():
    return f"""⏰ *OPENING CONFIRMATION*

📊 First 15-min Range Ready

🎯 Trade Rules:
• Break High → LONG
• Break Low → SHORT

⚡ Avoid fake breakout

⏰ {datetime.now().strftime('%H:%M:%S')}

⚠️ Informational only
"""


if __name__ == "__main__":
    send(FREE, free_msg())
    send(PREMIUM, premium_msg())

    print("✅ 9:20 sent")
