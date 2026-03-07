"""
Marketing Content - Automated promotional posts
"""

import os
import random
import logging  # ← ADD THIS LINE
from datetime import datetime
from src.telegram.poster import TelegramPoster

# Now this will work
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
        
        if hour == 9:  # 9 AM
            self.post_educational()
        elif hour == 11:  # 11 AM
            self.post_promotion()
        elif hour == 14:  # 2 PM
            self.post_promotion()
        elif hour == 16:  # 4 PM
            self.post_educational()
        
        print("\n=== MARKETING COMPLETE ===")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Starting Marketing...")
    marketing = MarketingContent()
    marketing.run()
    print("🏁 Marketing finished")
