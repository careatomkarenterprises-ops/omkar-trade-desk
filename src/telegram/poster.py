import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TelegramPoster:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

        self.channels = {
            'premium': os.getenv('CHANNEL_PREMIUM'),
            'free': os.getenv('CHANNEL_FREE'),
            'test': os.getenv('CHANNEL_TEST')
        }

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, channel, message):
        try:
            chat_id = self.channels.get(channel)

            if not chat_id:
                print(f"❌ Invalid channel: {channel}")
                return

            url = f"{self.base_url}/sendMessage"

            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print(f"✅ Message sent to {channel}")
            else:
                print(f"❌ Telegram Error: {response.text}")

        except Exception as e:
            print(f"❌ Error sending message: {e}")
