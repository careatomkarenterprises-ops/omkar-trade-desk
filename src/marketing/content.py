"""
Marketing Content - Automated promotional posts
"""

import os
import random
from datetime import datetime
from src.telegram.poster import TelegramPoster

class MarketingContent:
    """
    Generate and post marketing content
    """
    
    def __init__(self):
        self.poster = TelegramPoster()
        self.razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        
        # Educational tips
        self.educational_tips = [
            "📚 **Trading Tip:** Volume precedes price. Always look for volume spikes before breakouts.",
            "📚 **Risk Management:** Never risk more than 2% on a single trade.",
            "📚 **Psychology:** Trading is 10% strategy and 90% discipline.",
            "📚 **Trend Following:** The trend is your friend. Don't fight it.",
            "📚 **Support & Resistance:** Price tends to reverse at key levels.",
            "📚 **Moving Averages:** 20 EMA acts as dynamic support in uptrends.",
            "📚 **Breakout Trading:** Wait for volume confirmation before entering.",
            "📚 **Stop Loss:** A trade without SL is like driving without brakes.",
            "📚 **Position Sizing:** Calculate size based on stop loss, not greed.",
            "📚 **Market Phases:** Know if we're in accumulation or distribution."
        ]
        
        # Marketing hooks
        self.marketing_hooks = [
            "🚀 **Stop guessing, start knowing!** Our scanner finds patterns automatically.",
            "💰 **Time is money.** Let our AI scan 100 stocks while you focus on trading.",
            "📈 **Missed today's move?** Never miss another pattern with real-time alerts.",
            "🎯 **90% of traders miss volume patterns.** Don't be one of them.",
            "⚡ **Real-time alerts** on your phone. Entry, SL, Target - all automated.",
            "🏦 **Institutional-grade analysis** at retail prices.",
            "📊 **Multi-asset coverage:** Nifty, Bank Nifty, Gold, Crude, Forex.",
            "🔔 **Get alerts before breakout.** Not after. Be first.",
            "💎 **The difference between winners and losers?** Our scanner.",
            "📱 **Trade on the go.** Alerts work anywhere, anytime."
        ]
    
    def post_educational(self):
        """Post educational tip"""
        tip = random.choice(self.educational_tips)
        self.poster.send_message('education', tip)
        logger.info("Educational tip posted")
    
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
        self.poster.send_message('education', message)
        logger.info("Promotion posted")
    
    def post_results_showcase(self):
        """Post sample results from today"""
        message = f"""
📊 **TODAY'S SCANNER RESULTS**

Our scanner detected patterns in:
• Selected banking stocks
• Gold (volume spike)
• USD/INR (support bounce)

📈 **Real-time alerts available**

👉 [Try Scanner Free]({self.razorpay_link})
"""
        self.poster.send_message('education', message)
        logger.info("Results showcase posted")
    
    def run(self):
        """Run marketing tasks based on time"""
        hour = datetime.now().hour
        
        if hour == 9:  # 9 AM
            self.post_educational()
        elif hour == 11:  # 11 AM
            self.post_promotion()
        elif hour == 14:  # 2 PM
            self.post_results_showcase()
        elif hour == 16:  # 4 PM
            self.post_educational()

if __name__ == "__main__":
    import logging
    logger = logging.getLogger(__name__)
    
    marketing = MarketingContent()
    marketing.run()
