import requests

class TelegramPoster:
    def __init__(self):
        # 🔴 PUT YOUR BOT TOKEN HERE
        self.bot_token = "YOUR_BOT_TOKEN"

        # 🔴 PUT YOUR CHANNEL IDs HERE
        self.channels = {
            "free": "YOUR_FREE_CHANNEL_ID",
            "premium": "YOUR_PREMIUM_CHANNEL_ID"
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
