import os
import requests
from src.scanner.master_scanner import MasterScanner


def send_test_telegram():
    print("🔍 Running Telegram test...")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHANNEL_FREE_MAIN")

    if not bot_token or not chat_id:
        print("❌ Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": "✅ Intraday Scanner is LIVE and working 🚀"
    }

    try:
        response = requests.post(url, data=data)
        print("📩 Telegram Response:", response.text)
    except Exception as e:
        print("❌ Telegram Error:", str(e))


if __name__ == "__main__":
    print("🚀 Starting Intraday Scanner...")

    # Step 1: Telegram test (VERY IMPORTANT)
    send_test_telegram()

    try:
        scanner = MasterScanner()

        print("📊 Running FNO Scan...")
        scanner.scan_intraday_fno()

        print("🪙 Running Commodity Scan...")
        scanner.scan_commodity()

        print("⏳ Posting Delayed Patterns...")
        scanner.post_delayed_patterns()

        print("✅ Scanner execution completed")

    except Exception as e:
        print("❌ ERROR in scanner:", str(e))
