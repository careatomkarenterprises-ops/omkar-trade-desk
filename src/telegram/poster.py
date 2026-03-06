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
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
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
        
        self.disclaimer = """
        
━━━━━━━━━━━━━━━━━━━━
📚 **OMKAR ENTERPRISES**
⚠️ Educational purpose only. Not investment advice.
📊 Market investments are subject to risks."""
    
    def send_message(self, channel: str, message: str, parse_mode: str = 'Markdown') -> Dict:
        """
        Send message to a Telegram channel
        """
        try:
            chat_id = self.channels.get(channel)
            if not chat_id:
                logger.error(f"Unknown channel: {channel}")
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
                logger.info(f"Message sent to {channel}")
                return {'success': True, 'data': response.json()}
            else:
                logger.error(f"Failed to send: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_pattern(self, channel: str, pattern: Dict) -> Dict:
        """
        Post a pattern detection alert
        """
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
