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


# ============================
# TELEGRAM
# ============================
def send_message(channels, message):

    for ch in channels:

        if not ch:
            continue

        try:

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            payload = {
                "chat_id": ch,
                "text": message,
                "parse_mode": "Markdown"
            }

            requests.post(url, data=payload, timeout=10)

            print(f"✅ Sent to {ch}")

        except Exception as e:
            print("Telegram Error:", e)


# ============================
# MARKET STATE
# ============================
def get_market_state():

    states = [
        "BREAKOUT",
        "RANGE",
        "WEAK"
    ]

    return random.choice(states)


# ============================
# FREE MESSAGE
# ============================
def create_free_message(state):

    msg = "⏰ *9:20 MARKET UPDATE*\n\n"

    if state == "BREAKOUT":

        msg += "📊 Market showing breakout attempt\n"
        msg += "👉 Wait for confirmation candle\n"

    elif state == "WEAK":

        msg += "📊 Market showing weakness\n"
        msg += "👉 Avoid aggressive buying\n"

    else:

        msg += "📊 Market inside opening range\n"
        msg += "👉 No confirmation yet\n"

    msg += "\n🔐 Premium gives exact trade trigger"

    msg += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    return msg


# ============================
# PREMIUM MESSAGE
# ============================
def create_premium_message(state):

    msg = "🏦 *OPENING CONFIRMATION REPORT*\n\n"

    if state == "BREAKOUT":

        msg += "📈 Bullish breakout structure forming\n"
        msg += "🎯 Above opening high → LONG setup\n"

    elif state == "WEAK":

        msg += "📉 Weak structure detected\n"
        msg += "🎯 Below opening low → SHORT setup\n"

    else:

        msg += "📦 Range formation detected\n"
        msg += "🎯 Wait for clean breakout candle\n"

    msg += "\n⚡ Institutional Rule:\n"
    msg += "• No trade before confirmation\n"
    msg += "• Avoid fake breakouts\n"
    msg += "• Risk management mandatory\n"

    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

    msg += "\n\n⚠️ Educational purpose only"

    return msg


# ============================
# MAIN
# ============================
if __name__ == "__main__":

    print("🚀 Running Opening Confirmation")

    state = get_market_state()

    free_message = create_free_message(state)

    premium_message = create_premium_message(state)

    send_message(FREE_CHANNELS, free_message)

    send_message(PREMIUM_CHANNELS, premium_message)

    print("✅ 9:20 Confirmation Sent")
