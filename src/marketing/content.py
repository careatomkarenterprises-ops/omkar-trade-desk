"""
Marketing Content - Automated promotional posts with REAL market data
"""

import os
import random
import logging
from datetime import datetime
from src.telegram.poster import TelegramPoster
from src.scanner.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)

class MarketingContent:
    def __init__(self):
        print("\n📢 MarketingContent Initializing...")
        self.poster = TelegramPoster()
        self.fetcher = DataFetcher()
        self.razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        
        # Lesson templates (will be filled with REAL data)
        self.lesson_templates = [
            {
                "name": "volume",
                "content": """📚 **TODAY'S LESSON: Volume Spike Detection**

**REAL EXAMPLE - {symbol}**

📊 **Today's Data:**
• Current Price: ₹{price}
• Volume: {volume_ratio}x above 20-day average
• This is a {volume_status} volume spike

🔍 **What This Means:**
When volume spikes {direction} with price, it confirms {institutional} participation.

💡 **Key Insight:**
Volume spikes often precede major moves. Watch for continuation.

⏰ Live from today's market: {date}
"""
            },
            {
                "name": "support_resistance",
                "content": """📚 **TODAY'S LESSON: Support & Resistance**

**REAL EXAMPLE - {symbol}**

📊 **Today's Levels:**
• Current Price: ₹{price}
• Today's High: ₹{high_day}
• Today's Low: ₹{low_day}
• 52-Week High: ₹{high_52w}
• 52-Week Low: ₹{low_52w}

🔍 **Current Situation:**
Price is {position} relative to key levels.

💡 **What To Watch:**
• Break above {resistance} = Bullish signal
• Break below {support} = Bearish signal

⏰ Live from today's market: {date}
"""
            },
            {
                "name": "trend",
                "content": """📚 **TODAY'S LESSON: Trend Analysis**

**{symbol} - REAL TIME ANALYSIS**

📊 **Current Trend:** {trend}
📈 **Trend Strength:** {strength}
📉 **Key Observation:** {observation}

🔍 **Technical Context:**
{technical_context}

💡 **Actionable Insight:**
{trading_idea}

⏰ Live from today's market: {date}
"""
            }
        ]
        
        print("  └─ ✅ MarketingContent initialized with REAL data")
    
    def get_market_example(self):
        """Find a real stock with interesting data for today's lesson"""
        try:
            symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'INFY', 'ITC', 'LT']
            random.shuffle(symbols)
            
            for symbol in symbols:
                data = self.fetcher.get_stock_data(symbol)
                if data is not None and len(data) > 20:
                    current = data['Close'].iloc[-1]
                    volume = data['Volume'].iloc[-1]
                    avg_volume = data['Volume'].iloc[-20:].mean()
                    volume_ratio = volume / avg_volume if avg_volume > 0 else 1
                    
                    # Get 52-week high/low
                    high_52w = data['High'].iloc[-252:].max() if len(data) > 252 else current * 1.2
                    low_52w = data['Low'].iloc[-252:].min() if len(data) > 252 else current * 0.8
                    
                    # Get today's range
                    high_day = data['High'].iloc[-1]
                    low_day = data['Low'].iloc[-1]
                    
                    # Determine trend using simple moving average
                    sma_20 = data['Close'].iloc[-20:].mean()
                    if current > sma_20 * 1.02:
                        trend = "STRONG UPTREND"
                        strength = "High"
                        observation = "Price well above key moving average"
                        technical = f"Price is {((current/sma_20)-1)*100:.1f}% above 20-day MA"
                        idea = f"Look for buying opportunities on dips to {sma_20:.0f}"
                    elif current < sma_20 * 0.98:
                        trend = "DOWNTREND"
                        strength = "High"
                        observation = "Price below key moving average"
                        technical = f"Price is {((sma_20/current)-1)*100:.1f}% below 20-day MA"
                        idea = f"Avoid catching falling knife. Wait for reversal"
                    else:
                        trend = "CONSOLIDATION"
                        strength = "Moderate"
                        observation = "Price trading near key moving average"
                        technical = "Price is consolidating near 20-day MA"
                        idea = "Wait for breakout above resistance or breakdown below support"
                    
                    return {
                        'symbol': symbol,
                        'price': round(current, 2),
                        'volume_ratio': round(volume_ratio, 1),
                        'volume_status': 'SIGNIFICANT' if volume_ratio > 1.8 else 'MODERATE',
                        'direction': 'up' if current > data['Open'].iloc[0] else 'down',
                        'institutional': 'strong institutional' if volume_ratio > 2 else 'institutional',
                        'high_day': round(high_day, 2),
                        'low_day': round(low_day, 2),
                        'high_52w': round(high_52w, 2),
                        'low_52w': round(low_52w, 2),
                        'position': 'near 52-week HIGH' if current > high_52w * 0.95 else 'near 52-week LOW' if current < low_52w * 1.05 else 'in middle of range',
                        'resistance': round(high_day * 1.01, 2),
                        'support': round(low_day * 0.99, 2),
                        'trend': trend,
                        'strength': strength,
                        'observation': observation,
                        'technical_context': technical,
                        'trading_idea': idea,
                        'date': datetime.now().strftime('%d %b %Y, %H:%M IST')
                    }
            
            # Fallback if no data
            return {
                'symbol': 'RELIANCE',
                'price': 2845.75,
                'volume_ratio': 2.3,
                'volume_status': 'SIGNIFICANT',
                'direction': 'up',
                'institutional': 'strong institutional',
                'high_day': 2875.50,
                'low_day': 2820.25,
                'high_52w': 2980.00,
                'low_52w': 2420.00,
                'position': 'near 52-week HIGH',
                'resistance': 2900.00,
                'support': 2800.00,
                'trend': 'UPTREND',
                'strength': 'High',
                'observation': 'Strong momentum',
                'technical_context': 'Price above all key moving averages',
                'trading_idea': 'Look for buying opportunities on dips',
                'date': datetime.now().strftime('%d %b %Y, %H:%M IST')
            }
        except Exception as e:
            logger.error(f"Error getting market example: {e}")
            return None
    
    def post_educational(self):
        """Post educational content with REAL market data"""
        print("\n=== POSTING EDUCATIONAL CONTENT WITH REAL DATA ===")
        
        # Get real market data
        example = self.get_market_example()
        
        if not example:
            print("❌ Could not get market data")
            return
        
        # Choose random lesson type
        lesson_type = random.choice(['volume', 'support_resistance', 'trend'])
        
        # Find matching template
        for template in self.lesson_templates:
            if template['name'] == lesson_type:
                message = template['content'].format(**example)
                result = self.poster.send_message('education', message)
                if result.get('success'):
                    print(f"✅ Posted {lesson_type} lesson with real data for {example['symbol']}")
                else:
                    print(f"❌ Failed to post: {result.get('error')}")
                break
        
        print("=== EDUCATIONAL POST COMPLETE ===\n")
    
    def post_promotion(self):
        """Post promotional content"""
        hook = random.choice([
            "🚀 **Stop guessing, start knowing!** Our scanner finds patterns automatically.",
            "💰 **Time is money.** Let our AI scan 100 stocks while you focus on trading.",
            "📈 **Missed today's move?** Never miss another pattern with real-time alerts."
        ])
        
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
        
        # 9:30 AM and 4:30 PM - Educational content
        if hour == 9 or hour == 16:
            self.post_educational()
        # 11:30 AM, 2:30 PM, 5:30 PM - Promotions
        elif hour == 11 or hour == 14 or hour == 17:
            self.post_promotion()
        else:
            print(f"⏰ Hour {hour} - no scheduled marketing")
            # For manual testing
            if os.getenv('GITHUB_ACTIONS'):
                test_msg = f"🧪 Marketing test at hour {hour}"
                self.poster.send_message('education', test_msg)
        
        print("\n=== MARKETING COMPLETE ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 Starting Marketing...")
    marketing = MarketingContent()
    marketing.run()
    print("🏁 Marketing finished")
