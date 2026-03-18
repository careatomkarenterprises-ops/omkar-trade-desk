"""
News Aggregator - Fetches and posts market news with duplicate prevention
"""

import os
import json
import requests
import logging
import random
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

class NewsAggregator:
    """
    Fetch and post market news with duplicate prevention
    """
    
    def __init__(self):
        print("\n📰 NewsAggregator Initializing...")
        self.poster = TelegramPoster()
        self.api_key = os.getenv('NEWS_API_KEY')
        print(f"  ├─ NEWS_API_KEY exists: {'✅ YES' if self.api_key else '❌ NO'}")
        
        # Track posted news to avoid duplicates
        self.posted_file = Path('data/posted_news.json')
        self.posted_headlines = set()
        self.load_posted_news()
        
        # Sector keywords for accurate mapping - UPDATED for better currency detection
        self.sector_keywords = {
            'currency': ['rupee', 'usd/inr', 'dollar', 'forex', 'inr', 'exchange rate', 
                         'rbi intervention', 'usd', 'inr', 'dollar index', 'currency'],
            'banking': ['rbi', 'bank', 'interest rate', 'repo rate', 'npas', 'hdfc', 
                        'icici', 'sbi', 'kotak', 'axis', 'banking'],
            'it': ['tech', 'software', 'it services', 'infosys', 'tcs', 'wipro', 
                   'hcl', 'nasdaq', 'technology'],
            'commodity': ['gold', 'silver', 'crude', 'oil', 'commodity', 'metal', 
                          'copper', 'aluminium', 'zinc'],
            'economy': ['gdp', 'inflation', 'cpi', 'fiscal', 'budget', 'economy', 
                        'finance minister', 'economic', 'fed', 'interest rate', 
                        'us futures', 'dow futures', 'european markets']  # US Futures goes to economy
        }
        
        # Channel mapping - UPDATED: economy ONLY goes to education
        self.channel_map = {
            'currency': ['currency'],
            'banking': ['banknifty', 'fno'],
            'it': ['nifty', 'fno'],
            'commodity': ['commodity'],
            'economy': ['education']  # ← ONLY education channel for economy news!
        }
        
        # Fallback news templates with variety - UPDATED with more currency options
        self.fallback_templates = {
            'currency': [
                {"title": "USD/INR opens higher at 83.45", "desc": "Rupee weakens as dollar strengthens amid FII outflows."},
                {"title": "RBI likely to intervene near 83.50", "desc": "Central bank watching volatility, may step in to defend rupee."},
                {"title": "Forex reserves rise by $2.3 billion", "desc": "India's forex kitty provides comfortable buffer for RBI."},
                {"title": "Rupee trades in narrow range", "desc": "USD/INR consolidates between 83.40-83.55."},
                {"title": "Dollar index holds key level", "desc": "Dollar strength impacts emerging market currencies."}
            ],
            'economy': [
                {"title": "US Futures steady ahead of key data", "desc": "Markets await inflation numbers later this week."},
                {"title": "European markets close mixed", "desc": "Tech stocks lead gains in London, Frankfurt flat."},
                {"title": "Fed signals cautious approach", "desc": "US central bank watching economic data for rate cues."},
                {"title": "Global cues mixed", "desc": "Asian markets trade with mild gains, US futures flat."}
            ],
            'banking': [
                {"title": "Banking stocks lead rally", "desc": "Nifty Bank outperforms with 1% gains."},
                {"title": "RBI keeps rates unchanged", "desc": "Status quo maintained, focus on liquidity."}
            ],
            'commodity': [
                {"title": "Gold holds above $2000", "desc": "Safe-haven demand supports precious metal."},
                {"title": "Crude steady amid supply concerns", "desc": "Oil prices consolidate near recent highs."}
            ]
        }
        
        print("  └─ ✅ NewsAggregator initialized")
    
    def load_posted_news(self):
        """Load previously posted news to avoid duplicates"""
        if self.posted_file.exists():
            try:
                with open(self.posted_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.posted_headlines = set(json.load(f))
                        print(f"  ├─ Loaded {len(self.posted_headlines)} previously posted news items")
            except:
                self.posted_headlines = set()
    
    def save_posted_news(self):
        """Save posted news for future runs (keep last 100)"""
        try:
            # Convert to list, keep last 100, convert back to set
            headlines_list = list(self.posted_headlines)[-100:]
            with open(self.posted_file, 'w') as f:
                json.dump(headlines_list, f)
        except Exception as e:
            logger.error(f"Error saving posted news: {e}")
    
    def is_duplicate(self, headline: str) -> bool:
        """Check if we've already posted this news"""
        if headline in self.posted_headlines:
            return True
        self.posted_headlines.add(headline)
        self.save_posted_news()
        return False
    
    def fetch_real_news(self) -> List[Dict]:
        """Fetch real news from NewsAPI"""
        print("\n📡 Fetching real news...")
        try:
            if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
                print("  ├─ No valid API key, using fallback")
                return []
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'in',
                'category': 'business',
                'apiKey': self.api_key,
                'pageSize': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                print(f"  ├─ Found {len(articles)} articles")
                
                news_list = []
                for article in articles:
                    if article['title'] and '[Removed]' not in article['title']:
                        # Skip duplicates
                        if self.is_duplicate(article['title']):
                            print(f"  ├─ Skipping duplicate: {article['title'][:30]}...")
                            continue
                        
                        news_list.append({
                            'title': article['title'],
                            'description': article['description'] or 'Market update',
                            'source': article['source']['name'],
                            'time': datetime.now().strftime('%H:%M IST'),
                            'is_fallback': False
                        })
                
                return news_list
            else:
                print(f"  ├─ API failed with status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  ├─ Error: {e}")
            return []
    
    def generate_fallback_news(self) -> List[Dict]:
        """Generate contextual news with variety when API fails"""
        print("  ├─ Generating fallback news")
        now = datetime.now()
        hour = now.hour
        
        # Determine which news type to generate (weighted random)
        news_type = random.choices(
            ['currency', 'economy', 'banking', 'commodity'],
            weights=[0.4, 0.3, 0.2, 0.1]  # 40% currency, 30% economy, etc.
        )[0]
        
        # Pick random template from the selected type
        template = random.choice(self.fallback_templates[news_type])
        
        # Create a unique key to avoid duplicates
        unique_key = f"{news_type}_{template['title']}_{now.strftime('%Y%m%d_%H')}"
        
        if self.is_duplicate(unique_key):
            # If already posted recently, pick another template
            all_templates = []
            for templates in self.fallback_templates.values():
                all_templates.extend(templates)
            template = random.choice(all_templates)
        
        return [{
            'title': template['title'],
            'description': template['desc'],
            'source': random.choice(['Omkar Scanner', 'Market Watch', 'TradeDesk', 'Global Market Watch']),
            'time': now.strftime('%H:%M IST'),
            'is_fallback': True
        }]
    
    def determine_sector(self, news_item: Dict) -> List[str]:
        """Determine which sectors are affected (accurate mapping)"""
        text = (news_item['title'] + ' ' + news_item['description']).lower()
        affected = []
        
        # Check for currency keywords first (highest priority)
        currency_keywords = ['rupee', 'usd/inr', 'dollar', 'forex', 'inr', 'exchange rate', 
                             'rbi intervention', 'currency', 'dollar index']
        if any(keyword in text for keyword in currency_keywords):
            affected.append('currency')
            return affected  # If currency, that's it - don't add other sectors
        
        # Check other sectors
        for sector, keywords in self.sector_keywords.items():
            if sector == 'currency':  # Already checked
                continue
            if any(keyword in text for keyword in keywords):
                affected.append(sector)
        
        # If no specific sector found, check for generic market terms
        if not affected:
            market_terms = ['market', 'nifty', 'sensex', 'stock', 'share', 'bse', 'nse']
            if any(term in text for term in market_terms):
                affected.append('economy')
            else:
                affected.append('economy')  # Default to economy
        
        # Remove duplicates
        return list(set(affected))
    
    def post_news(self):
        """Fetch and post news to relevant channels"""
        print("\n=== STARTING NEWS POSTING ===")
        
        # Try to fetch real news first
        news_items = self.fetch_real_news()
        
        # If no real news, use fallback
        if not news_items:
            news_items = self.generate_fallback_news()
        
        print(f"📰 Total news items to post: {len(news_items)}")
        
        for item in news_items:
            print(f"\n--- News Item ---")
            print(f"Title: {item['title'][:50]}...")
            
            sectors = self.determine_sector(item)
            print(f"Affected sectors: {sectors}")
            
            # Determine channels to post to
            channels_to_post = set()
            for sector in sectors:
                if sector in self.channel_map:
                    for ch in self.channel_map[sector]:
                        channels_to_post.add(ch)
            
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
