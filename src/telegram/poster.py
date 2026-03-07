"""
Telegram Poster - Sends messages to channels
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class TelegramPoster:
    """
    Post messages to Telegram channels
    """
    
    def __init__(self):
        # Debug: Print environment info
        print("🔍 TelegramPoster Initializing...")
        
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        print(f"  ├─ TELEGRAM_BOT_TOKEN exists: {'✅ YES' if self.bot_token else '❌ NO'}")
        
        if self.bot_token:
            print(f"  ├─ Token length: {len(self.bot_token)}")
            print(f"  ├─ Token starts with: {self.bot_token[:10]}...")
        else:
            print("  └─ ❌ FATAL: No token found!")
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        print(f"  ├─ Base URL created")
        
        # Channel IDs (from secrets)
        self.channels = {
            'premium': os.getenv('CHANNEL_PREMIUM', '-1003707680362'),
            'nifty': os.getenv('CHANNEL_NIFTY', '-1003666021620'),
            'banknifty': os.getenv('CHANNEL_BANKNIFTY', '-1003550746662'),
            'commodity': os.getenv('CHANNEL_COMMODITY', '-1003743209615'),
            'currency': os.getenv('CHANNEL_CURRENCY', '-1003845581337'),
            'education': os.getenv('CHANNEL_EDUCATION', '-1003787192138'),
            'swing': os.getenv('CHANNEL_SWING', '-1003799906343'),
            'intraday': os.getenv('CHANNEL_INTRADAY', '-1003780662199'),
            'fno': os.getenv('CHANNEL_FNO', '-1003827790111')
        }
        
        # Verify channels
        print(f"  ├─ Channels configured: {list(self.channels.keys())}")
        for name, chat_id in self.channels.items():
            print(f"  │   {name}: {chat_id[:5]}...{chat_id[-5:] if chat_id else 'MISSING'}")
        
        self.disclaimer = """
        
━━━━━━━━━━━━━━━━━━━━
📚 **OMKAR ENTERPRISES**
⚠️ Educational purpose only. Not investment advice.
📊 Market investments are subject to risks."""
        
        print("  └─ ✅ TelegramPoster initialized successfully")
    
    def send_message(self, channel: str, message: str, parse_mode: str = 'Markdown') -> Dict:
        """
        Send message to a Telegram channel
        """
        print(f"\n📤 Sending message to channel: {channel}")
        
        try:
            chat_id = self.channels.get(channel)
            if not chat_id:
                print(f"  └─ ❌ Unknown channel: {channel}")
                return {'success': False, 'error': 'Unknown channel'}
            
            print(f"  ├─ Chat ID: {chat_id[:5]}...{chat_id[-5:]}")
            print(f"  ├─ Message length: {len(message)} chars")
            print(f"  ├─ Parse mode: {parse_mode}")
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message + self.disclaimer,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            print(f"  ├─ Making API request...")
            response = requests.post(url, json=payload, timeout=15)
            
            print(f"  ├─ Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ├─ Telegram API response: {result.get('ok')}")
                if result.get('ok'):
                    print(f"  └─ ✅ Message sent successfully!")
                    logger.info(f"Message sent to {channel}")
                    return {'success': True, 'data': result}
                else:
                    print(f"  └─ ❌ Telegram error: {result.get('description')}")
                    return {'success': False, 'error': result.get('description')}
            else:
                print(f"  └─ ❌ HTTP error: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"  └─ ❌ Exception: {str(e)}")
            logger.error(f"Error sending message: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_pattern(self, channel: str, pattern: Dict) -> Dict:
        """
        Post a pattern detection alert
        """
        print(f"\n🔍 Posting pattern to {channel}")
        message = f"""
🔍 **PATTERN DETECTED - Omkar Scanner**

🎯 **{pattern['symbol']}**
📊 **Pattern:** {pattern['primary_pattern']}
📈 **Strength:** {pattern['strength']*100:.0f}%

💰 **Price:** ₹{pattern['price']}
📊 **Volume:** {pattern['volume_ratio']}x avg
⏰ **Time:** {pattern['time']}

👉 **Full access:** omkar.in/scanner
"""
        return self.send_message(channel, message)
    
    def post_market_update(self, update: str) -> Dict:
        """
        Post market update to education channel
        """
        print(f"\n📊 Posting market update")
        message = f"""
📊 **MARKET UPDATE**

{update}

⏰ {datetime.now().strftime('%d %b %Y, %H:%M IST')}

📈 **Live Dashboard:** omkar.in/scanner
"""
        return self.send_message('education', message)
    
    def post_promotion(self) -> Dict:
        """
        Post promotional content with payment link
        """
        print(f"\n📢 Posting promotion")
        razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        
        message = f"""
📢 **Omkar Scanner Premium**

✅ Real-time pattern detection
✅ Multi-asset coverage
✅ 30-min updates during market hours
✅ Educational content

🔥 **Limited Offer:** ₹999/month

👉 [Subscribe Now]({razorpay_link})

━━━━━━━━━━━━━━━━━━━━
✨ Join 100+ serious traders
"""
        return self.send_message('education', message)
