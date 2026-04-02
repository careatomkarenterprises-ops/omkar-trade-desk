"""
Smart News Aggregator - Persistent duplicate prevention + daily limit
"""

import os
import json
import requests
import logging
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from pathlib import Path

from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

class NewsAggregator:
    """
    Fetch and post news with cross‑run duplicate prevention and daily limit.
    """
    
    # Keywords that MUST be present for a news to be considered (Indian market focus)
    INDIAN_KEYWORDS = [
        'nifty', 'sensex', 'bank nifty', 'indian market', 'india', 'rupee',
        'rbi', 'sebi', 'modi', 'finance minister', 'indian economy',
        'bse', 'nse', 'indian stock', 'indian rupee'
    ]
    
    HIGH_IMPACT_KEYWORDS = [
        'rbi', 'repo rate', 'interest rate', 'mpc', 'monetary policy',
        'fed', 'federal reserve', 'rate cut', 'rate hike', 'crr', 'slr',
        'gdp', 'inflation', 'cpi', 'wpi', 'iip', 'trade deficit',
        'budget', 'finance minister', 'nirmala sitharaman', 'tax', 'gst',
        'nifty', 'sensex', 'bank nifty', 'all-time high', '52-week high',
        '52-week low', 'fii', 'dii', 'fpi', 'institutional buying',
        'crude oil', 'brent crude', 'gold price', 'silver price',
        'npa', 'bad loan', 'credit growth'
    ]
    
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
        print("\n📰 Persistent News Aggregator Initializing...")
        self.poster = TelegramPoster()
        self.api_key = os.getenv('NEWS_API_KEY')
        
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.posted_file = self.data_dir / 'posted_news.json'
        self.daily_counter_file = self.data_dir / 'daily_post_count.json'
        
        self.posted_hashes = set()
        self.load_posted_news()
        
        self.daily_count = 0
        self.load_daily_count()
        
        print("  ├─ Cross‑run duplicate prevention: ENABLED (cache)")
        print("  ├─ Daily post limit: 8 posts/day")
        print("  └─ ✅ Persistent News Aggregator initialized")
    
    def load_posted_news(self):
        """Load previously posted news hashes from cache file."""
        if self.posted_file.exists():
            try:
                with open(self.posted_file, 'r') as f:
                    data = json.load(f)
                    self.posted_hashes = set(data)
                    print(f"  ├─ Loaded {len(self.posted_hashes)} previously posted news hashes")
            except:
                self.posted_hashes = set()
        else:
            self.posted_hashes = set()
    
    def save_posted_news(self):
        """Save posted news hashes to cache file."""
        try:
            # Keep only last 500 to avoid file bloat
            hashes_list = list(self.posted_hashes)[-500:]
            with open(self.posted_file, 'w') as f:
                json.dump(hashes_list, f)
        except Exception as e:
            logger.error(f"Error saving posted news: {e}")
    
    def load_daily_count(self):
        """Load today's post count from cache file."""
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
        """Save today's post count to cache file."""
        try:
            with open(self.daily_counter_file, 'w') as f:
                json.dump({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'count': self.daily_count
                }, f)
        except:
            pass
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize news title to ignore small wording differences.
        Example: "RBI says banks cannot offer NDF contracts" and
                 "RBI tightens rules governing FX derivatives" will become similar.
        """
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove common stop words that don't change meaning
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'of', 'to', 'for', 'on', 'at', 'by', 'with', 'without'}
        words = text.split()
        words = [w for w in words if w not in stop_words]
        # Keep only first 80 characters (sufficient for deduplication)
        normalized = ' '.join(words)[:80]
        return normalized
    
    def get_content_hash(self, title: str) -> str:
        """Generate a hash of the normalized title for duplicate detection."""
        normalized = self.normalize_text(title)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def is_duplicate(self, title: str) -> bool:
        """Check if similar news has already been posted."""
        content_hash = self.get_content_hash(title)
        if content_hash in self.posted_hashes:
            return True
        self.posted_hashes.add(content_hash)
        self.save_posted_news()
        return False
    
    def is_high_impact(self, title: str, description: str) -> Tuple[bool, int, str]:
        """Check if news is relevant to Indian markets and has sufficient impact."""
        text = (title + ' ' + description).lower()
        
        # Must contain at least one Indian market keyword
        if not any(kw in text for kw in self.INDIAN_KEYWORDS):
            return False, 0, None
        
        impact_score = 0
        matched = None
        for kw in self.HIGH_IMPACT_KEYWORDS:
            if kw in text:
                if kw in ['rbi', 'repo rate', 'fed', 'rate cut', 'rate hike']:
                    impact_score = 10
                elif kw in ['gdp', 'inflation', 'budget', 'nifty', 'sensex']:
                    impact_score = 9
                elif kw in ['crude oil', 'gold price', 'rupee']:
                    impact_score = 8
                elif kw in ['fii', 'dii', 'results', 'earnings']:
                    impact_score = 7
                else:
                    impact_score = max(impact_score, 6)
                matched = kw
                break
        
        # Only post if impact >= 7
        return impact_score >= 7, impact_score, matched
    
    def can_post_today(self) -> bool:
        """Check if daily limit (8 posts) has been reached."""
        return self.daily_count < 8
    
    def increment_daily_count(self):
        """Increment daily post counter and save."""
        self.daily_count += 1
        self.save_daily_count()
    
    def fetch_filtered_news(self) -> List[Dict]:
        """Fetch news from NewsAPI and filter for high‑impact Indian market stories."""
        print("\n📡 Fetching news from NewsAPI...")
        if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
            print("  ├─ No valid API key")
            return []
        
        try:
            from_date = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d")
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': '(India OR Nifty OR RBI OR rupee) AND (market OR economy OR stock)',
                'from': from_date,
                'sortBy': 'relevancy',
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
            print(f"  ├─ Total articles: {len(articles)}")
            
            filtered = []
            for art in articles:
                if not art['title'] or '[Removed]' in art['title']:
                    continue
                # Skip duplicates based on normalized title
                if self.is_duplicate(art['title']):
                    print(f"  ├─ ⏭️ DUPLICATE: {art['title'][:60]}...")
                    continue
                
                is_impactful, score, match = self.is_high_impact(art['title'], art.get('description', ''))
                if is_impactful and self.can_post_today():
                    print(f"  ├─ ✅ IMPACT {score}: {art['title'][:60]}...")
                    filtered.append({
                        'title': art['title'],
                        'description': art.get('description', 'Market update')[:400],
                        'source': art['source']['name'],
                        'time': datetime.now().strftime('%H:%M IST'),
                        'impact_score': score,
                        'matched_keyword': match
                    })
                    self.increment_daily_count()
                else:
                    print(f"  ├─ ⏭️ LOW IMPACT: {art['title'][:60]}...")
            
            return filtered
        except Exception as e:
            print(f"  ├─ Error: {e}")
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
        print("=== PERSISTENT NEWS FILTER ACTIVE ===")
        print("="*60)
        
        items = self.fetch_filtered_news()
        if not items:
            print("\n📭 No high‑impact Indian market news found.")
            print("   (Better no news than spam.)")
            return
        
        print(f"\n📰 Posting {len(items)} item(s) (Daily total: {self.daily_count}/8)\n")
        for item in items:
            sectors = self.determine_sector(item)
            urgency = "🔴 URGENT" if item['impact_score'] >= 9 else "🟠 IMPORTANT" if item['impact_score'] >= 8 else "🟡 NOTEWORTHY"
            channels = set()
            for s in sectors:
                channels.update(self.CHANNEL_MAP.get(s, []))
            channels = list(channels)[:2]  # Max 2 channels per story
            
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
    print("🚀 Starting Persistent News Aggregator...")
    news = NewsAggregator()
    news.post_news()
    print("🏁 Finished")