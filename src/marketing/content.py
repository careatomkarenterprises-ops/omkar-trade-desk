"""
Marketing Content - Automated promotional posts
ONLY posts to @OmkarEducation channel
"""

import os
import random
import logging
from datetime import datetime
from typing import Dict, Optional
import pandas as pd
import numpy as np

from src.telegram.poster import TelegramPoster
from src.scanner.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)

class MarketingContent:
    def __init__(self):
        print("\n" + "="*60)
        print("📢 MARKETING CONTENT INITIALIZATION")
        print("="*60)
        
        self.poster = TelegramPoster()
        self.fetcher = DataFetcher()
        self.razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        
        # Stock list
        self.stock_list = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY', 'SBIN', 'ITC', 'LT',
            'SUNPHARMA', 'AXISBANK', 'KOTAKBANK', 'HCLTECH', 'MARUTI', 'TITAN', 'WIPRO'
        ]
        
        # Lesson templates
        self.lesson_templates = [
            {
                "name": "volume",
                "content": """📚 **TODAY'S LESSON: Volume Spike Detection**

**REAL EXAMPLE - {symbol}** {data_source_badge}

📊 **Today's Data:**
• Current Price: ₹{price}
• Volume: {volume_ratio}x above 20-day average
• This is a {volume_status} volume spike

🔍 **What This Means:**
When volume spikes {direction} with price, it confirms {institutional} participation.

💡 **Key Insight:**
{key_insight}

⏰ Live from today's market: {date}
"""
            },
            {
                "name": "support_resistance",
                "content": """📚 **TODAY'S LESSON: Support & Resistance**

**REAL EXAMPLE - {symbol}** {data_source_badge}

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

**{symbol} - REAL TIME ANALYSIS** {data_source_badge}

📊 **Current Trend:** {trend}
📈 **Trend Strength:** {strength}/10
📉 **Key Observation:** {observation}

🔍 **Technical Context:**
{technical_context}

💡 **Actionable Insight:**
{trading_idea}

⏰ Live from today's market: {date}
"""
            }
        ]
        
        print("  ├─ Stock list: {} stocks loaded".format(len(self.stock_list)))
        print("  └─ ✅ MarketingContent initialized (Education channel only)")
    
    def format_volume(self, volume: int) -> str:
        """Format volume in lakhs/crores"""
        if volume >= 10000000:
            return f"{volume/10000000:.1f}Cr"
        elif volume >= 100000:
            return f"{volume/100000:.1f}L"
        else:
            return str(volume)
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate RSI"""
        try:
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return round(rsi.iloc[-1], 1) if not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    def get_market_example(self) -> Optional[Dict]:
        """Find a real stock with interesting data"""
        try:
            random.shuffle(self.stock_list)
            
            for symbol in self.stock_list:
                try:
                    data = self.fetcher.get_stock_data(symbol)
                    
                    if data is None or len(data) < 30:
                        continue
                    
                    data_source = getattr(data, 'attrs', {}).get('source', 'yahoo')
                    is_zerodha = data_source == 'zerodha'
                    is_mock = data_source == 'mock'
                    
                    current = data['Close'].iloc[-1]
                    volume = data['Volume'].iloc[-1]
                    avg_volume = data['Volume'].iloc[-20:].mean()
                    volume_ratio = volume / avg_volume if avg_volume > 0 else 1
                    
                    high_52w = data['High'].iloc[-252:].max() if len(data) > 252 else current * 1.3
                    low_52w = data['Low'].iloc[-252:].min() if len(data) > 252 else current * 0.7
                    
                    high_day = data['High'].iloc[-1]
                    low_day = data['Low'].iloc[-1]
                    
                    sma_20 = data['Close'].rolling(20).mean().iloc[-1]
                    rsi = self.calculate_rsi(data)
                    
                    if current > sma_20 * 1.02 and rsi > 60:
                        trend = "STRONG UPTREND"
                        strength = 8
                        observation = "Strong bullish momentum"
                        technical = f"Price {((current/sma_20)-1)*100:.1f}% above 20-day MA"
                        idea = f"Look for buying opportunities on dips"
                    elif current < sma_20 * 0.98 and rsi < 40:
                        trend = "STRONG DOWNTREND"
                        strength = 8
                        observation = "Strong selling pressure"
                        technical = f"Price {((sma_20/current)-1)*100:.1f}% below 20-day MA"
                        idea = "Wait for reversal confirmation"
                    elif current > sma_20:
                        trend = "UPTREND"
                        strength = 6
                        observation = "Gradual uptrend"
                        technical = "Price above key moving average"
                        idea = "Accumulate on dips"
                    elif current < sma_20:
                        trend = "DOWNTREND"
                        strength = 6
                        observation = "Downward pressure"
                        technical = "Price below key moving average"
                        idea = "Wait for reversal"
                    else:
                        trend = "CONSOLIDATION"
                        strength = 4
                        observation = "Range-bound action"
                        technical = "Price consolidating"
                        idea = "Wait for breakout"
                    
                    # Volume status
                    if volume_ratio > 2.0:
                        volume_status = "SIGNIFICANT (2x+)"
                        institutional = "strong institutional"
                        key_insight = f"Volume {volume_ratio:.1f}x average indicates major institutional activity"
                    elif volume_ratio > 1.5:
                        volume_status = "ABOVE AVERAGE"
                        institutional = "institutional"
                        key_insight = "Above-average volume suggests active participation"
                    else:
                        volume_status = "NORMAL"
                        institutional = "normal"
                        key_insight = "Volume is within normal range"
                    
                    if current > high_52w * 0.95:
                        position = f"near 52-week HIGH"
                    elif current < low_52w * 1.05:
                        position = f"near 52-week LOW"
                    else:
                        position = "in middle of range"
                    
                    # Data source badge
                    if is_zerodha:
                        source_badge = "🔵 [Zerodha Live Data]"
                        note = ""
                    elif is_mock:
                        source_badge = "🟡 [Simulated Data]"
                        note = "\n⚠️ **Note:** Using simulated data - live APIs temporarily unavailable"
                    else:
                        source_badge = "🟢 [Yahoo Finance]"
                        note = ""
                    
                    return {
                        'symbol': symbol,
                        'price': round(current, 2),
                        'volume_ratio': round(volume_ratio, 1),
                        'volume_status': volume_status,
                        'avg_volume_formatted': self.format_volume(avg_volume),
                        'direction': 'up' if current > data['Open'].iloc[0] else 'down',
                        'institutional': institutional,
                        'high_day': round(high_day, 2),
                        'low_day': round(low_day, 2),
                        'high_52w': round(high_52w, 2),
                        'low_52w': round(low_52w, 2),
                        'position': position,
                        'resistance': round(high_day * 1.01, 2),
                        'support': round(low_day * 0.99, 2),
                        'trend': trend,
                        'strength': strength,
                        'observation': observation,
                        'technical_context': technical,
                        'trading_idea': idea,
                        'rsi': rsi,
                        'key_insight': key_insight,
                        'data_source_badge': source_badge,
                        'note': note,
                        'date': datetime.now().strftime('%d %b %Y, %H:%M IST')
                    }
                except Exception as e:
                    continue
            
            return self.get_fallback_data()
            
        except Exception as e:
            logger.error(f"Error in get_market_example: {e}")
            return self.get_fallback_data()
    
    def get_fallback_data(self) -> Dict:
        """Generate fallback data"""
        import random
        symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
        symbol = random.choice(symbols)
        price = random.uniform(1000, 3000)
        
        return {
            'symbol': symbol,
            'price': round(price, 2),
            'volume_ratio': round(1.5 + random.random(), 1),
            'volume_status': 'ABOVE AVERAGE',
            'avg_volume_formatted': '12.5L',
            'direction': 'up' if random.random() > 0.5 else 'down',
            'institutional': 'institutional',
            'high_day': round(price * 1.02, 2),
            'low_day': round(price * 0.98, 2),
            'high_52w': round(price * 1.3, 2),
            'low_52w': round(price * 0.7, 2),
            'position': 'mid-range',
            'resistance': round(price * 1.02, 2),
            'support': round(price * 0.98, 2),
            'trend': 'UPTREND',
            'strength': 6,
            'observation': 'Price showing strength',
            'technical_context': 'Technical indicators suggest bullish momentum',
            'trading_idea': f'Look for buying opportunities near {round(price * 0.98, 2)}',
            'rsi': 65,
            'key_insight': 'Volume patterns suggest institutional accumulation',
            'data_source_badge': "🟡 [Estimated Data]",
            'note': "\n⚠️ **Note:** Live data temporarily limited. Showing estimated values.",
            'date': datetime.now().strftime('%d %b %Y, %H:%M IST')
        }
    
    def post_educational(self):
        """Post educational content - ONLY to education channel"""
        print("\n" + "="*60)
        print("📢 POSTING EDUCATIONAL CONTENT")
        print("="*60)
        
        example = self.get_market_example()
        
        if not example:
            print("❌ Could not get market data")
            return
        
        source = "Zerodha" if "Zerodha" in example.get('data_source_badge', '') else "Yahoo"
        print(f"📊 Data source: {source}")
        print(f"📈 Symbol: {example['symbol']} @ ₹{example['price']}")
        
        lesson_type = random.choice(['volume', 'support_resistance', 'trend'])
        print(f"📚 Lesson type: {lesson_type}")
        
        for template in self.lesson_templates:
            if template['name'] == lesson_type:
                message = template['content'].format(**example)
                # ✅ ONLY send to education channel
                result = self.poster.send_message('education', message)
                if result.get('success'):
                    print(f"✅ Posted {lesson_type} lesson to @OmkarEducation")
                else:
                    print(f"❌ Failed to post: {result.get('error')}")
                break
        
        print("="*60 + "\n")
    
    def post_promotion(self):
        """Post promotional content - ONLY to education channel"""
        hooks = [
            ("🚀", "Stop guessing, start knowing! Our scanner finds patterns automatically."),
            ("💰", "Time is money. Let our AI scan 100 stocks while you focus on trading."),
            ("📈", "Missed today's move? Never miss another pattern with real-time alerts.")
        ]
        
        emoji, hook = random.choice(hooks)
        
        message = f"""
{emoji} **{hook}**

✨ **What you get:**
✅ Real-time pattern alerts
✅ Multi-asset coverage (Stocks, Commodities, Forex)
✅ 30-min updates during market hours
✅ Educational content daily with real examples
✅ Technical indicator analysis

🔥 **Limited Offer:** ₹999/month

👉 [Join Premium - ₹999/month]({self.razorpay_link})

━━━━━━━━━━━━━━━━━━━━
✨ Join 100+ serious traders who never miss a move
"""
        # ✅ ONLY send to education channel
        return self.poster.send_message('education', message)
    
    def run(self):
        """Run marketing tasks based on time"""
        print("\n" + "="*60)
        print("🚀 MARKETING WORKFLOW STARTED")
        print("="*60)
        
        hour = datetime.now().hour
        print(f"⏰ Current hour: {hour}")
        
        if hour == 9 or hour == 16:
            self.post_educational()
        elif hour == 11 or hour == 14 or hour == 17:
            self.post_promotion()
        else:
            print(f"⏰ Hour {hour} - no scheduled marketing")
            if os.getenv('GITHUB_ACTIONS'):
                test_msg = f"🧪 Marketing test at hour {hour}"
                self.poster.send_message('education', test_msg)
        
        print("="*60 + "\n")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 Starting Marketing...")
    marketing = MarketingContent()
    marketing.run()
    print("🏁 Marketing finished")
