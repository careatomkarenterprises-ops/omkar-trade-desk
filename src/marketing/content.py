"""
Marketing Content - Automated promotional posts
"""

import os
import random
from datetime import datetime
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

class MarketingContent:
    def __init__(self):
        print("\n📢 MarketingContent Initializing...")
        self.poster = TelegramPoster()
        self.razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        
        self.educational_tips = [
            "📚 **Trading Tip:** Volume precedes price. Always look for volume spikes before breakouts."
        ]
        
        self.marketing_hooks = [
            "🚀 **Stop guessing, start knowing!** Our scanner finds patterns automatically."
        ]
        print("  └─ ✅ MarketingContent initialized")
    
    def send_test_message(self):
        """Send a test message to verify"""
        print("\n🧪 SENDING TEST MESSAGE FROM MARKETING...")
        test_msg = f"""
🧪 **MARKETING TEST MESSAGE**

If you see this, the marketing workflow is working!

✅ GitHub Actions
✅ Telegram Bot
✅ Channel Access

⏰ {datetime.now().strftime('%H:%M IST')}
"""
        return self.poster.send_message('education', test_msg)
    
    def post_educational(self):
        """Post educational tip"""
        tip = random.choice(self.educational_tips)
        return self.poster.send_message('education', tip)
    
    def post_promotion(self):
        """Post promotional content"""
        hook = random.choice(self.marketing_hooks)
        message = f"""
{hook}

✨ **What you get:**
✅ Real-time pattern alerts
✅ Multi-asset coverage
✅ 30-min updates during market
✅ Educational content daily

👉 [Join Premium - ₹999/month]({self.razorpay_link})

━━━━━━━━━━━━━━━━━━━━
🔥 Limited time offer
"""
        return self.poster.send_message('education', message)
    
    def run(self):
        """Run marketing tasks"""
        print("\n=== STARTING MARKETING ===")
        
        # Send test message first
        test_result = self.send_test_message()
        
        if test_result.get('success'):
            print("✅ Test successful, sending actual content...")
            # Then send regular content
            self.post_promotion()
        else:
            print("❌ Test failed, check logs above")
        
        print("\n=== MARKETING COMPLETE ===")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("🚀 Starting Marketing...")
    marketing = MarketingContent()
    marketing.run()
    print("🏁 Marketing finished")
