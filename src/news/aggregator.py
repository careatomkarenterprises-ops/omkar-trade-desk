"""
Smart News Aggregator - EXTREME FILTERING
Only posts news that ACTUALLY matters to Indian traders
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
    Smart news filter - posts ONLY high-impact, Indian-market relevant news
    """
    
    # INDIAN MARKET ONLY - No international news unless impactful
    INDIAN_KEYWORDS = [
        'nifty', 'sensex', 'bank nifty', 'indian market', 'india', 'rupee', 
        'rbi', 'sebi', 'modi', 'finance minister', 'indian economy',
        'bse', 'nse', 'indian stock', 'indian rupee', 'india\'s'
    ]
    
    # HIGH IMPACT KEYWORDS - Only news containing these will be posted
    HIGH_IMPACT_KEYWORDS = [
        # Central Bank & Policy
        'rbi', 'repo rate', 'interest rate', 'mpc', 'monetary policy',
        'fed', 'federal reserve', 'rate cut', 'rate hike', 'crr', 'slr',
        
        # Economic Data
        'gdp', 'inflation', 'cpi', 'wpi', 'iip', 'industrial production',
        'trade deficit', 'current account', 'fiscal deficit',
        
        # Government Policy
        'budget', 'finance minister', 'nirmala sitharaman', 'tax', 'gst',
        'sebi', 'new policy',
        
        # Market Moving
        'nifty', 'sensex', 'bank nifty', 'all-time high', '52-week high',
        '52-week low', 'fii', 'dii', 'fpi', 'institutional buying',
        'bulk deal', 'block deal', 'results', 'earnings',
        
        # Commodities
        'crude oil', 'brent crude', 'gold price', 'silver price',
        
        # Banking
        'npa', 'bad loan', 'credit growth', 'deposit growth'
    ]
    
    # SECTORS
    SECTOR_KEYWORDS = {
        'banking': ['rbi', 'bank', 'npa', 'npas', 'bank nifty', 'sbi', 'hdfc', 'icici'],
        'it': ['tcs', 'infosys', 'wipro', 'hcl', 'tech', 'software', 'it services'],
        'commodity': ['gold', 'silver', 'crude', 'oil', 'commodity'],
        'currency': ['rupee', 'usd/inr', 'dollar', 'forex', 'inr'],
        'economy': ['gdp', 'inflation', 'budget', 'economy', 'fiscal']
    }
    
    # CHANNEL MAPPING
    CHANNEL_MAP = {
        'banking': ['banknifty', 'fno'],
        'it': ['nifty', 'fno'],
        'commodity': ['commodity'],
        'currency': ['currency'],
        'economy': ['education', 'nifty']
    }
    
    def __init__(self):
        print("\n📰 Extreme News Filter Initializing...")
        self.poster = TelegramPoster()
        self.api_key = os.getenv('NEWS_API_KEY')
        
        # Track posted news by content hash (not just title)
        self.posted_file = Path('data/posted_news.json')
        self.posted_hashes = set()
        self.load_posted_news()
        
        # Track daily post count
        self.daily_post_file = Path('data/daily_post_count.json')
        self.daily_count = 0
        self.load_daily_count()
        
        print("  ├─ INDIAN MARKET ONLY filter: ENABLED")
        print("  ├─ MAX 8 posts per day limit")
        print("  └─ ✅ Extreme News Filter initialized")
    
    def load_posted_news(self):
        """Load previously posted news by hash"""
        if self.posted_file.exists():
            try:
                with open(self.posted_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.posted_hashes = set(json.load(f))
                        print(f"  ├─ Loaded {len(self.posted_hashes)} posted news hashes")
            except:
                self.posted_hashes = set()
    
    def save_posted_news(self):
        """Save posted news hashes"""
        try:
            hashes_list = list(self.posted_hashes)[-500:]  # Keep last 500
            with open(self.posted_file, 'w') as f:
                json.dump(hashes_list, f)
        except:
            pass
    
    def load_daily_count(self):
        """Load today's post count"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.daily_post_file.exists():
            try:
                with open(self.daily_post_file, 'r') as f:
                    data = json.load(f)
                    if data.get('date') == today:
                        self.daily_count = data.get('count', 0)
                    else:
                        self.daily_count = 0
            except:
                self.daily_count = 0
        else:
            self.daily_count = 0
    
    def save_daily_count(self):
        """Save today's post count"""
        try:
            with open(self.daily_post_file, 'w') as f:
                json.dump({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'count': self.daily_count
                }, f)
        except:
            pass
    
    def get_content_hash(self, title: str, description: str) -> str:
        """Create unique hash for news content (ignores source variations)"""
        # Normalize the content
        import re
        normalized = title.lower()
        # Remove common variations
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Get first 100 chars as key
        content_key = normalized[:100]
        return hashlib.md5(content_key.encode()).hexdigest()
    
    def is_duplicate_content(self, title: str, description: str) -> bool:
        """Check if same content already posted (even from different sources)"""
        content_hash = self.get_content_hash(title, description)
        if content_hash in self.posted_hashes:
            return True
        self.posted_hashes.add(content_hash)
        self.save_posted_news()
        return False
    
    def is_indian_market_news(self, title: str, description: str) -> bool:
        """Check if news is relevant to Indian markets"""
        text = (title + ' ' + description).lower()
        for keyword in self.INDIAN_KEYWORDS:
            if keyword in text:
                return True
        return False
    
    def is_high_impact(self, title: str, description: str) -> Tuple[bool, int, str]:
        """Check if news is HIGH IMPACT for Indian traders"""
        text = (title + ' ' + description).lower()
        
        # MUST be Indian market news
        if not self.is_indian_market_news(title, description):
            return False, 0, None
        
        impact_score = 0
        matched_keyword = None
        
        for keyword in self.HIGH_IMPACT_KEYWORDS:
            if keyword in text:
                if keyword in ['rbi', 'repo rate', 'fed', 'rate cut']:
                    impact_score = 10
                elif keyword in ['gdp', 'inflation', 'budget', 'nifty', 'sensex']:
                    impact_score = 9
                elif keyword in ['crude oil', 'gold price', 'rupee']:
                    impact_score = 8
                elif keyword in ['fii', 'dii', 'results', 'earnings']:
                    impact_score = 7
                else:
                    impact_score = max(impact_score, 6)
                matched_keyword = keyword
                break
        
        # Only post if impact score >= 7 (VERY HIGH threshold)
        return impact_score >= 7, impact_score, matched_keyword
    
    def is_todays_news(self, published_at: str) -> bool:
        """Check if news is from today"""
        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            today = datetime.now().date()
            return pub_date.date() == today
        except:
            return True
    
    def can_post_today(self) -> bool:
        """Check if we haven't exceeded daily limit"""
        if self.daily_count >= 8:  # Max 8 posts per day total
            print(f"  ├─ Daily limit reached ({self.daily_count}/8), skipping")
            return False
        return True
    
    def increment_daily_count(self):
        """Increment daily post counter"""
        self.daily_count += 1
        self.save_daily_count()
    
    def fetch_filtered_news(self) -> List[Dict]:
        """Fetch and filter ONLY high-impact Indian market news"""
        print("\n📡 Fetching news...")
        
        if not self.api_key or self.api_key == 'YOUR_API_KEY_HERE':
            print("  ├─ No API key")
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
            print(f"  ├─ Found {len(articles)} total articles")
            
            high_impact_news = []
            
            for article in articles:
                if not article['title'] or '[Removed]' in article['title']:
                    continue
                
                # Check for duplicate content (same news from different sources)
                if self.is_duplicate_content(article['title'], article.get('description', '')):
                    print(f"  ├─ ⏭️ DUPLICATE: {article['title'][:50]}...")
                    continue
                
                # Check if high impact for Indian markets
                is_impactful, impact_score, matched = self.is_high_impact(
                    article['title'], 
                    article.get('description', '')
                )
                
                if is_impactful and self.can_post_today():
                    print(f"  ├─ ✅ HIGH IMPACT: {article['title'][:60]}... (Score: {impact_score})")
                    high_impact_news.append({
                        'title': article['title'],
                        'description': article.get('description', 'Market update'),
                        'source': article['source']['name'],
                        'time': datetime.now().strftime('%H:%M IST'),
                        'impact_score': impact_score,
                        'matched_keyword': matched,
                        'published': article.get('publishedAt', '')
                    })
                    self.increment_daily_count()
                else:
                    print(f"  ├─ ⏭️ LOW IMPACT: {article['title'][:50]}...")
            
            return high_impact_news
            
        except Exception as e:
            print(f"  ├─ Error: {e}")
            return []
    
    def determine_sector(self, news_item: Dict) -> List[str]:
        """Determine affected sectors"""
        text = (news_item['title'] + ' ' + news_item['description']).lower()
        affected = []
        
        for sector, keywords in self.SECTOR_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                affected.append(sector)
        
        if not affected:
            affected.append('economy')
        
        return list(set(affected))
    
    def calculate_urgency(self, impact_score: int) -> str:
        """Determine urgency level"""
        if impact_score >= 9:
            return "🔴 URGENT - Market Moving"
        elif impact_score >= 8:
            return "🟠 IMPORTANT - Watch Closely"
        else:
            return "🟡 NOTEWORTHY - Be Aware"
    
    def post_news(self):
        """Post ONLY high-impact news to channels"""
        print("\n" + "="*60)
        print("=== EXTREME NEWS FILTERING ACTIVE ===")
        print("="*60)
        
        # Reset daily counter if needed
        self.load_daily_count()
        
        news_items = self.fetch_filtered_news()
        
        if not news_items:
            print("\n📭 No high-impact Indian market news found.")
            print("   (Better no news than spam news)")
            return
        
        print(f"\n📰 Posting {len(news_items)} high-impact items (Daily limit: {self.daily_count}/8)\n")
        
        for item in news_items:
            print(f"--- IMPACT: {item['impact_score']}/10 ---")
            print(f"Title: {item['title'][:80]}...")
            
            sectors = self.determine_sector(item)
            urgency = self.calculate_urgency(item['impact_score'])
            
            channels_to_post = set()
            for sector in sectors:
                if sector in self.CHANNEL_MAP:
                    for ch in self.CHANNEL_MAP[sector]:
                        channels_to_post.add(ch)
            
            # Limit to MAX 2 channels per news (avoid spam)
            channels_to_post = list(channels_to_post)[:2]
            
            print(f"Urgency: {urgency}")
            print(f"Channels: {channels_to_post}")
            
            message = f"""
{urgency}

📰 **MARKET NEWS UPDATE**

**{item['title']}**

{item['description']}

🔍 **Source:** {item['source']}
⏰ **Time:** {item['time']}
📊 **Impact:** {item['impact_score']}/10
🎯 **Sector:** {', '.join(sectors)}
"""
            
            for channel in channels_to_post:
                result = self.poster.send_message(channel, message)
                if result.get('success'):
                    print(f"  ✅ Posted to {channel}")
                else:
                    print(f"  ❌ Failed to {channel}")
            
            print()
        
        print("=== POSTING COMPLETE ===")

if __name__ == "__main__":
    print("🚀 Starting Extreme News Filter...")
    news = NewsAggregator()
    news.post_news()
    print("🏁 Finished")