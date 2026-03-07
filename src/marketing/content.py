"""
Marketing Content - Automated promotional posts
"""

import os
import random
import logging
from datetime import datetime
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

class MarketingContent:
    def __init__(self):
        print("\n📢 MarketingContent Initializing...")
        self.poster = TelegramPoster()
        self.razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        
        self.educational_tips = [
            "📚 **Trading Tip:** Volume precedes price. Always look for volume spikes before breakouts.",
            "📚 **Risk Management:** Never risk more than 2% of your capital on a single trade.",
            "📚 **Psychology:** Trading is 10% strategy and 90% discipline."
        ]
        
        self.marketing_hooks = [
            "🚀 **Stop guessing, start knowing!** Our scanner finds patterns automatically.",
            "💰 **Time is money.** Let our AI scan 100 stocks while you focus on trading.",
            "📈 **Missed today's move?** Never miss another pattern with real-time alerts."
        ]
        print("  └─ ✅ MarketingContent initialized")
    
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
        """Run marketing tasks based on time"""
        print("\n=== STARTING MARKETING ===")
        hour = datetime.now().hour
        
        if hour == 9 or hour == 16:  # 9 AM and 4 PM
            self.post_educational()
        elif hour == 11 or hour == 14 or hour == 17:  # 11 AM, 2 PM, 5 PM
            self.post_promotion()
        else:
            print(f"⏰ Hour {hour} - no scheduled marketing")
            # Send test message if manually triggered
            if os.getenv('GITHUB_ACTIONS'):  # If running in GitHub
                test_msg = f"🧪 Marketing test at hour {hour}"
                self.poster.send_message('education', test_msg)
    
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 Starting Marketing...")
    marketing = MarketingContent()
    marketing.run()
    print("🏁 Marketing finished")
