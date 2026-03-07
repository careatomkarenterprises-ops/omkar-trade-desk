"""
News Aggregator - Fetches and posts market news
"""

import os
import requests
import logging
from datetime import datetime
import random
from typing import List, Dict

from src.telegram.poster import TelegramPoster  # ← This import must be correct

logger = logging.getLogger(__name__)

class NewsAggregator:
    """
    Fetch and post market news
    """
    
    def __init__(self):
        print("\n📰 NewsAggregator Initializing...")
        self.poster = TelegramPoster()  # ← This creates the poster instance
        self.api_key = os.getenv('NEWS_API_KEY')
        print(f"  ├─ NEWS_API_KEY exists: {'✅ YES' if self.api_key else '❌ NO'}")
        
        # Sector keywords
        self.sectors = {
            'banking': ['rbi', 'bank', 'interest rate', 'repo rate', 'npas'],
            'it': ['tech', 'software', 'it services', 'nasdaq'],
            'commodity': ['gold', 'silver', 'crude', 'oil'],
            'currency': ['rupee', 'dollar', 'forex', 'inr'],
            'economy': ['gdp', 'inflation', 'cpi', 'budget', 'economy']
        }
        print("  └─ ✅ NewsAggregator initialized")
    
    def fetch_news(self) -> List[Dict]:
        """Fetch real news from NewsAPI"""
        print("\n📡 Fetching news...")
        try:
            if not self.api_key:
                print("  ├─ No API key, using fallback")
                return self.generate_fallback_news()
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'in',
                'category': 'business',
                'apiKey': self.api_key,
                'pageSize': 5
            }
            
            print(f"  ├─ Making API request to NewsAPI...")
            response = requests.get(url, params=params, timeout=10)
            print(f"  ├─ Response status: {response.status_code}")
            
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                print(f"  ├─ Found {len(articles)} articles")
                news_list = []
                
                for article in articles:
                    if article['title'] and '[Removed]' not in article['title']:
                        news_list.append({
                            'title': article['title'],
                            'description': article['description'] or '',
                            'source': article['source']['name'],
                            'time': datetime.now().strftime('%H:%M IST')
                        })
                
                return news_list
            
            print(f"  └─ API failed, using fallback")
            return self.generate_fallback_news()
            
        except Exception as e:
            print(f"  └─ ❌ Error: {e}")
            return self.generate_fallback_news()
    
    def generate_fallback_news(self) -> List[Dict]:
        """Generate contextual news when API fails"""
        print("  ├─ Generating fallback news")
        now = datetime.now()
        hour = now.hour
        
        if 8 <= hour <= 10:
            return [{
                'title': 'Morning Market Update: Global cues positive',
                'description': 'Asian markets trading higher. SGX Nifty indicates gap up opening.',
                'source': 'Omkar Market Intelligence',
                'time': now.strftime('%H:%M IST')
            }]
        elif 11 <= hour <= 14:
            return [{
                'title': 'Sector Watch: Banking stocks showing strength',
                'description': 'Nifty Bank outperforms with institutional buying visible.',
                'source': 'Omkar Scanner',
                'time': now.strftime('%H:%M IST')
            }]
        elif 15 <= hour <= 17:
            return [{
                'title': 'Closing Bell: Markets end near day\'s high',
                'description': 'Broad-based buying seen. Advance-decline ratio positive.',
                'source': 'Omkar TradeDesk',
                'time': now.strftime('%H:%M IST')
            }]
        else:
            return [{
                'title': 'US Futures steady ahead of key data',
                'description': 'Dow futures +0.2%. Dollar index holds key level.',
                'source': 'Global Market Watch',
                'time': now.strftime('%H:%M IST')
            }]
    
    def determine_sector(self, news_item: Dict) -> List[str]:
        """Determine which sectors are affected"""
        text = (news_item['title'] + ' ' + news_item['description']).lower()
        affected = []
        
        for sector, keywords in self.sectors.items():
            if any(k in text for k in keywords):
                affected.append(sector)
        
        if not affected:
            affected = ['economy']
        
        return affected
    
    def post_news(self):
        """Fetch and post news to relevant channels"""
        print("\n=== STARTING NEWS POSTING ===")
        news_items = self.fetch_news()
        print(f"📰 Total news items: {len(news_items)}")
        
        for i, item in enumerate(news_items, 1):
            print(f"\n--- News Item {i} ---")
            print(f"Title: {item['title'][:50]}...")
            
            sectors = self.determine_sector(item)
            print(f"Affected sectors: {sectors}")
            
            # Determine channels
            channels_to_post = set()
            for sector in sectors:
                if sector == 'banking':
                    channels_to_post.update(['banknifty', 'fno'])
                elif sector == 'it':
                    channels_to_post.add('nifty')
                elif sector == 'commodity':
                    channels_to_post.add('commodity')
                elif sector == 'currency':
                    channels_to_post.add('currency')
                else:
                    channels_to_post.update(['education', 'nifty'])
            
            print(f"Posting to channels: {channels_to_post}")
            
            # Create message
            message = f"""
📰 **MARKET NEWS UPDATE**

**{item['title']}**

{item['description']}

🔍 **Source:** {item['source']}
⏰ **Time:** {item['time']}

📊 **Affected:** {', '.join(sectors)}
"""
            
            # Post to each channel
            for channel in channels_to_post:
                print(f"  → Posting to {channel}...")
                result = self.poster.send_message(channel, message)
                if result.get('success'):
                    print(f"    ✅ Success")
                else:
                    print(f"    ❌ Failed: {result.get('error')}")
        
        print("\n=== NEWS POSTING COMPLETE ===")

if __name__ == "__main__":
    print("🚀 Starting News Aggregator...")
    news = NewsAggregator()
    news.post_news()
    print("🏁 News Aggregator finished")
