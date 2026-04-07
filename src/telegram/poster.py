"""
Telegram Poster - Sends messages and photos to channels
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class TelegramPoster:
    """
    Post messages and photos to Telegram channels
    """
    
    def __init__(self):
        print("\n" + "="*60)
        print("🔍 TELEGRAM POSTER INITIALIZATION")
        print("="*60)
        
        # Check token
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        print(f"\n📌 TELEGRAM_BOT_TOKEN:")
        print(f"  ├─ Exists: {'✅ YES' if self.bot_token else '❌ NO'}")
        if self.bot_token:
            print(f"  ├─ Length: {len(self.bot_token)} characters")
            print(f"  ├─ First 10 chars: {self.bot_token[:10]}...")
            print(f"  ├─ Last 10 chars: ...{self.bot_token[-10:]}")
        
        if not self.bot_token:
            print("  └─ ❌ FATAL: No token found!")
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        print(f"\n📌 Base URL: {self.base_url[:50]}...")
        
        # Test bot authentication
        print(f"\n📌 Testing bot authentication...")
        try:
            test_url = f"{self.base_url}/getMe"
            test_response = requests.get(test_url, timeout=10)
            print(f"  ├─ Response status: {test_response.status_code}")
            if test_response.status_code == 200:
                bot_info = test_response.json()
                if bot_info.get('ok'):
                    bot_user = bot_info.get('result', {}).get('username', 'unknown')
                    print(f"  ├─ Bot username: @{bot_user}")
                    print(f"  └─ ✅ Bot is valid and reachable!")
                else:
                    print(f"  └─ ❌ Bot error: {bot_info.get('description')}")
            else:
                print(f"  └─ ❌ HTTP error: {test_response.text}")
        except Exception as e:
            print(f"  └─ ❌ Exception: {e}")
        
        # Channel IDs
        print(f"\n📌 Channel IDs (from secrets/env):")
        self.channels = {
            'premium': os.getenv('CHANNEL_PREMIUM'),
            'nifty': os.getenv('CHANNEL_NIFTY'),
            'banknifty': os.getenv('CHANNEL_BANKNIFTY'),
            'commodity': os.getenv('CHANNEL_COMMODITY'),
            'currency': os.getenv('CHANNEL_CURRENCY'),
            'education': os.getenv('CHANNEL_EDUCATION'),
            'swing': os.getenv('CHANNEL_SWING'),
            'intraday': os.getenv('CHANNEL_INTRADAY'),
            'fno': os.getenv('CHANNEL_FNO')
        }
        
        for name, chat_id in self.channels.items():
            print(f"  ├─ {name}: ", end='')
            if chat_id:
                print(f"{chat_id[:5]}...{chat_id[-5:]} (length: {len(chat_id)})")
            else:
                print(f"❌ MISSING")
        
        # Test channel access (education channel)
        print(f"\n📌 Testing channel access (education channel):")
        if self.channels.get('education'):
            test_channel = self.channels['education']
            try:
                get_chat_url = f"{self.base_url}/getChat"
                payload = {'chat_id': test_channel}
                chat_response = requests.post(get_chat_url, json=payload, timeout=10)
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    if chat_data.get('ok'):
                        chat_info = chat_data.get('result', {})
                        print(f"  ├─ Chat title: {chat_info.get('title', 'unknown')}")
                        print(f"  └─ ✅ Bot has access to this channel!")
                    else:
                        print(f"  └─ ❌ Chat error: {chat_data.get('description')}")
                else:
                    print(f"  └─ ❌ HTTP error: {chat_response.text}")
            except Exception as e:
                print(f"  └─ ❌ Exception: {e}")
        else:
            print(f"  └─ ❌ No education channel ID configured")
        
       self.disclaimer = """

━━━━━━━━━━━━━━━━━━━━
📚 *Omkar Market Intelligence*

⚠️ This platform provides AI-based market insights for educational purposes only.
❗ We do NOT provide investment advice or recommendations.
📊 Market investments are subject to risk.
"""
        
        print("\n" + "="*60)
        print("✅ TelegramPoster initialization complete")
        print("="*60 + "\n")
    
    def send_message(self, channel: str, message: str, parse_mode: str = 'Markdown') -> Dict:
        """
        Send message to a Telegram channel
        """
        try:
            chat_id = self.channels.get(channel)
            if not chat_id:
                print(f"❌ Unknown channel: {channel}")
                return {'success': False, 'error': 'Unknown channel'}
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message + self.disclaimer,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ Message sent to {channel}")
                    logger.info(f"Message sent to {channel}")
                    return {'success': True, 'data': result}
                else:
                    return {'success': False, 'error': result.get('description')}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_photo(self, channel: str, photo_path: str, caption: str = "") -> Dict:
        """
        Send a photo to Telegram channel with optional caption
        """
        try:
            chat_id = self.channels.get(channel)
            if not chat_id:
                return {'success': False, 'error': 'Unknown channel'}
            
            if not os.path.exists(photo_path):
                return {'success': False, 'error': 'Photo file not found'}
            
            url = f"{self.base_url}/sendPhoto"
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': chat_id,
                    'caption': caption + self.disclaimer,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info(f"Photo sent to {channel}")
                    return {'success': True, 'data': result}
                else:
                    return {'success': False, 'error': result.get('description')}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_pattern(self, channel: str, pattern: Dict) -> Dict:
        """
        Post a pattern detection alert to specific channel
        """
        message = f"""
🔍 **PATTERN DETECTED - Omkar Scanner**

🎯 **{pattern['symbol']}**
📊 **Pattern:** {pattern['primary_pattern']}
📈 **Strength:** {pattern['strength']*100:.0f}%
📊 **Trend:** {pattern.get('trend', 'neutral').upper()}

💰 **Price:** ₹{pattern['price']}
📊 **Volume:** {pattern['volume_ratio']}x avg
⏰ **Time:** {pattern['time']}

👉 **Full access:** omkar.in/scanner
"""
        return self.send_message(channel, message)
    
    def post_market_update(self, update: str) -> Dict:
        """
        Post market update to education channel only
        """
        message = f"""
📊 **MARKET UPDATE**

{update}

⏰ {datetime.now().strftime('%d %b %Y, %H:%M IST')}

📈 **Live Dashboard:** omkar.in/scanner
"""
        return self.send_message('education', message)
    
    def post_promotion(self, razorpay_link: str = None) -> Dict:
        """
        Post promotional content to education channel only
        """
        if not razorpay_link:
            razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        
        message = f"""
📢 **Omkar Scanner Premium**

✅ Real-time pattern detection
✅ Multi-asset coverage
✅ 30-min updates during market hours
✅ Educational content daily

🔥 **Limited Offer:** ₹999/month

👉 [Subscribe Now]({razorpay_link})

━━━━━━━━━━━━━━━━━━━━
✨ Join 100+ serious traders
"""
        return self.send_message('education', message)
