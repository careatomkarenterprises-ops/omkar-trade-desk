import os
import logging
from datetime import datetime
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# CONFIG
# ================================
API_KEY = os.getenv("KITE_API_KEY")
ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_FREE_MAIN")

# ================================
# TELEGRAM FUNCTION
# ================================
import requests

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

# ================================
# PRE-MARKET LOGIC
# ================================
def run_premarket_scan():
    try:
        kite = KiteConnect(api_key=API_KEY)
        kite.set_access_token(ACCESS_TOKEN)

        logger.info("✅ Connected to Zerodha")

        # Get instruments
        instruments = kite.instruments("NSE")

        # Filter some liquid stocks (top 100 approx)
        symbols = [i['tradingsymbol'] for i in instruments if i['segment'] == 'NSE' and i['instrument_type'] == 'EQ'][:100]

        movers = []

        for symbol in symbols:
            try:
                data = kite.ltp(f"NSE:{symbol}")
                price = data[f"NSE:{symbol}"]["last_price"]

                # Dummy logic (replace later with real pre-open logic)
                movers.append((symbol, price))

            except:
                continue

        # Sort top gainers/losers (dummy)
        movers = sorted(movers, key=lambda x: x[1], reverse=True)

        top_gainers = movers[:5]
        top_losers = movers[-5:]

        # ============================
        # FORMAT MESSAGE
        # ============================
        message = "📊 *PRE-MARKET SCANNER*\n\n"

        message += "🚀 *Top Gainers*\n"
        for s in top_gainers:
            message += f"• {s[0]} - ₹{s[1]}\n"

        message += "\n🔻 *Top Losers*\n"
        for s in top_losers:
            message += f"• {s[0]} - ₹{s[1]}\n"

        message += f"\n⏰ Time: {datetime.now().strftime('%H:%M:%S')}"

        send_telegram_message(message)

        logger.info("✅ Telegram message sent")

    except Exception as e:
        logger.error(f"❌ Error: {e}")

# ================================
# RUN
# ================================
if __name__ == "__main__":
    run_premarket_scan()
