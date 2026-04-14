import os
import requests

class TelegramPoster:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channels = {
            'currency': os.getenv('CHANNEL_CURRENCY'),
            'commodity': os.getenv('CHANNEL_COMMODITY'),
            'fno': os.getenv('CHANNEL_FNO'),
            'swing': os.getenv('CHANNEL_SWING')
        }
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, channel, message):
        chat_id = self.channels.get(channel.lower())
        if not chat_id:
            print(f"⚠️ Warning: No Chat ID for {channel}")
            return
        
        url = f"{self.base_url}/sendMessage"
        payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Success: Posted to {channel}")
            else:
                print(f"❌ Telegram Error: {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

def send_to_telegram(segment, message):
    poster = TelegramPoster()
    poster.send_message(segment, message)
