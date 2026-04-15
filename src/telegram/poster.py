import os
import requests

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
        chat_id = self.channels.get(channel.lower())

        if not chat_id:
            print(f"❌ Channel '{channel}' not configured")
            return

        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print(f"✅ Message sent to {channel}")
            else:
                print(f"❌ Telegram API Error: {response.text}")

        except Exception as e:
            print(f"❌ Connection Error: {e}")
