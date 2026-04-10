"""
Smart News Aggregator - Event‑based deduplication + Extended Freshness
"""

import os
import json
import requests
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from pathlib import Path

from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

class NewsAggregator:
    """
    Fetch and post news with event‑based duplicate prevention and 18‑hour freshness.
    """
    
    # Keywords that MUST be present for Indian market relevance
    INDIAN_KEYWORDS = [
        'nifty', 'sensex', 'bank nifty', 'indian market', 'india', 'rupee',
        'rbi', 'sebi', 'modi', 'finance minister', 'indian economy',
        'bse', 'nse', 'indian stock', 'indian rupee', 'trent', 'reliance'
    ]
    
    HIGH_IMPACT_KEYWORDS = {
        10: ['rbi', 'repo rate', 'interest rate', 'mpc', 'monetary policy',
             'fed', 'federal reserve', 'rate cut', 'rate hike', 'crr', 'slr'],
        9:  ['gdp', 'inflation', 'cpi', 'wpi', 'iip', 'trade deficit', 'budget',
             'nifty', 'sensex', 'bank nifty', 'all-time high', '52-week high'],
        8:  ['crude oil', 'brent crude', 'gold price', 'silver price', 'rupee'],
        7:  ['fii', 'dii', 'fpi', 'institutional buying', 'results', 'earnings']
    }
    
    SECTOR_KEYWORDS = {
        'banking': ['rbi', 'bank', 'npa', 'npas', 'bank nifty', 'sbi', 'hdfc', 'icici'],
        'it': ['tcs', 'infosys', 'wipro', 'hcl', 'tech', 'software', 'it services'],
        'commodity': ['gold', 'silver', 'crude', 'oil', 'commodity'],
        'currency': ['rupee', 'usd/inr', 'dollar', 'forex', 'inr'],
        'economy': ['gdp', 'inflation', 'budget', 'economy', 'fiscal']
    }
    
    CHANNEL_MAP = {
        'banking': ['banknifty', 'fno'],
        'it': ['nifty', 'fno'],
        'commodity': ['commodity'],
        'currency': ['currency'],
        'economy': ['education', 'nifty']
    }
    
    def __init__(self):
        print("\n📰 Event‑based News Aggregator Initializing...")
        self.poster = TelegramPoster()
        self.api_key = os.getenv('NEWS_API_KEY')
        
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.posted_file = self.data_dir / 'posted_news.json'
        self.daily_counter_file = self.data_dir / 'daily_post_count.json'
        
        self.posted_events = set()   
        self.load_posted_news()
        
        self.daily_count = 0
        self.load_daily_count()
        
        print("  ├─ Event‑based deduplication: ENABLED")
        print("  ├─ Freshness filter: only news from last 18 hours") # Updated
        print("  ├─ Daily post limit: 8 posts/day")
        print("  └─ ✅ Ready")
    
    def load_posted_news(self):
        if self.posted_file.exists():
            try:
                with open(self.posted_file, 'r') as f:
                    data = json.load(f)
                    self.posted_events = set(data)
                    print(f"  ├─ Loaded {len(self.posted_events)} previously posted events")
            except:
                self.posted_events = set()
        else:
            self.posted_events = set()
    
    def save_posted_news(self):
        try:
            # Keep last 500 to keep file small
            hashes_list = list(self.posted_events)[-500:]
            with open(self.posted_file, 'w') as f:
                json.dump(hashes_list, f)
        except Exception as e:
            logger.error(f"Error saving posted news: {e}")
    
    def load_daily_count(self):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.daily_counter_file.exists():
            try:
                with open(self.daily_counter_file, 'r') as f:
                    data = json.load(f)
                    if data.get('date') == today:
                        self.daily_count = data.get('count', 0)
                    else:
                        self.daily_count = 0
            except:
                self.daily_count = 0
        else:
            self.daily_count = 0
        print(f"  ├─ Today's post count: {self.daily_count}/8")
    
    def save_daily_count(self):
        try:
            with open(self.daily_counter_file, 'w') as f:
                json.dump({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'count': self.daily_count
                }, f)
        except:
            pass
    
    def extract_event_key(self, title: str) -> str:
        text = title.lower()
        fluff = ['source:', 'update:', 'live:', 'today', 'morning report', 'headlines']
        for f in fluff:
            text = text.replace(f, '')
        return text[:80].strip()
    
    def get_event_hash(self, title: str) -> str:
        event_key = self.extract_event_key(title)
        return hashlib.md5(event_key.encode()).hexdigest()
    
    def is_duplicate_event(self, title: str) -> bool:
        event_hash = self.get_event_hash(title)
        return event_hash in self.posted_events
    
    def is_fresh(self, published_at: str) -> bool:
        """Check if article was published in the last 18 hours."""
        try:
            pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.now().astimezone()
            age = now - pub_time
            return age.total_seconds() <= 18 * 3600  # Increased to 18 hours
        except:
            return True
    
    def calculate_impact(self, title: str, description: str) -> Tuple[int, str]:
        text = (title + ' ' + description).lower()
        for score, keywords in self.HIGH_IMPACT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return score, kw
        return 7, 'general'
    
    def is_relevant(self, title: str, description: str) -> bool:
        text = (title + ' ' + description).lower()
        return any(kw in text for kw in self.INDIAN_KEYWORDS)
    
    def can_post_today(self) -> bool:
        return self.daily_count < 8
    
    def increment_daily_count(self):
        self.daily_count += 1
        self.save_daily_count()
    
    def fetch_filtered_news(self) -> List[Dict]:
        print("\n📡 Fetching fresh news from NewsAPI...")
        if not self.api_key:
            print("  ├─ No valid API key found in environment")
            return []
        
        try:
            from_date = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
            url = "https://newsapi.org/v2/everything"
            
            # Optimized Query for Indian Markets
            query = '("Indian stock market" OR Nifty50 OR "RBI" OR "Sensex")'
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'language': 'en',
                'pageSize': 50
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code != 200:
                print(f"  ├─ API error: {response.status_code}")
                return []
            
            data = response.json()
            articles = data.get('articles', [])
            print(f"  ├─ Total articles fetched: {len(articles)}")
            
            filtered = []
            for art in articles:
                if not art['title'] or '[Removed]' in art['title']:
                    continue
                
                # Check Relevancy
                if not self.is_relevant(art['title'], art.get('description', '')):
                    continue
                
                # Check Freshness (18h)
                if not self.is_fresh(art['publishedAt']):
                    continue
                
                # Check Deduplication (The hash memory)
                if self.is_duplicate_event(art['title']):
                    continue
                
                # Check Daily Limit
                if not self.can_post_today():
                    print(f"  ├─ ⏭️ DAILY LIMIT REACHED ({self.daily_count}/8)")
                    break
                
                impact_score, matched = self.calculate_impact(art['title'], art.get('description', ''))
                
                # Add to memory before returning to prevent double-processing in one run
                event_hash = self.get_event_hash(art['title'])
                self.posted_events.add(event_hash)
                
                filtered.append({
                    'title': art['title'],
                    'description': art.get('description', 'Market update')[:400],
                    'source': art['source']['name'],
                    'time': datetime.now().strftime('%H:%M IST'),
                    'impact_score': impact_score,
                    'matched_keyword': matched,
                    'published_at': art['publishedAt']
                })
                self.increment_daily_count()
            
            self.save_posted_news() # Persist the new hashes to disk
            return filtered
            
        except Exception as e:
            print(f"  ├─ Error during fetch: {e}")
            return []
    
    def determine_sector(self, news_item: Dict) -> List[str]:
        text = (news_item['title'] + ' ' + news_item['description']).lower()
        sectors = []
        for sector, keywords in self.SECTOR_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                sectors.append(sector)
        return list(set(sectors)) if sectors else ['economy']
    
    def post_news(self):
        print("\n" + "="*60)
        print("=== EVENT‑BASED NEWS FILTER ACTIVE ===")
        print("="*60)
        
        items = self.fetch_filtered_news()
        if not items:
            print("\n📭 No fresh, high‑impact news found in this cycle.")
            return
        
        print(f"\n📰 Posting {len(items)} item(s) (Daily total: {self.daily_count}/8)\n")
        for item in items:
            sectors = self.determine_sector(item)
            urgency = "🔴 URGENT" if item['impact_score'] >= 9 else "🟠 IMPORTANT" if item['impact_score'] >= 8 else "🟡 NOTEWORTHY"
            
            channels = set()
            for s in sectors:
                channels.update(self.CHANNEL_MAP.get(s, []))
            channels = list(channels)[:2]  
            
            message = f"""
{urgency} - Market Moving

📰 **MARKET NEWS UPDATE**

**{item['title']}**

{item['description']}

🔍 **Source:** {item['source']}
⏰ **Time:** {item['time']}
📊 **Impact:** {item['impact_score']}/10
🎯 **Sector:** {', '.join(sectors)}
"""
            for ch in channels:
                res = self.poster.send_message(ch, message)
                if res.get('success'):
                    print(f"  ✅ Posted to {ch}")
                else:
                    print(f"  ❌ Failed to {ch}")
            print()
        
        print("=== POSTING COMPLETE ===")

if __name__ == "__main__":
    print("🚀 Starting Event‑based News Aggregator...")
    news = NewsAggregator()
    news.post_news()
    print("🏁 Finished")
