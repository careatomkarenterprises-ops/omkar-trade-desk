import os
import requests

class TelegramPoster:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channels = {
            'currency': os.getenv('CHANNEL_CURRENCY'),
            'fno': os.getenv('CHANNEL_FNO'),
            'swing': os.getenv('CHANNEL_SWING'),
            'commodity': os.getenv('CHANNEL_COMMODITY')
        }
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, channel, message):
        chat_id = self.channels.get(channel.lower())
        if not chat_id:
            print(f"⚠️ ERROR: No ID found for {channel} in GitHub Secrets")
            return
        
        url = f"{self.base_url}/sendMessage"
        payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
        
        print(f"📡 Sending to {channel} (ID: {chat_id})...")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: Message appeared in Telegram!")
        else:
            print(f"❌ TELEGRAM REJECTED: {response.text}")

def send_to_telegram(segment, message):
    poster = TelegramPoster()
    poster.send_message(segment, message)
