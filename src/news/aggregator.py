"""
Omkar Trade Services - Elite News Aggregator (Merged & Hardened)
"""

import os
import json
import requests
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from src.telegram.poster import TelegramPoster

class NewsAggregator:
    # 1. QUALITY GATE: High-Authority Indian Finance Sources Only
    FINANCE_DOMAINS = "moneycontrol.com,economictimes.indiatimes.com,financialexpress.com,business-standard.com,livemint.com"

    # 2. SECTOR MAPPING (Keeping your original logic)
    SECTOR_KEYWORDS = {
        'banking': ['rbi', 'bank', 'npa', 'hdfc', 'sbi', 'icici', 'axis', 'banknifty'],
        'it': ['tcs', 'infosys', 'wipro', 'hcl', 'tech'],
        'commodity': ['gold', 'silver', 'crude', 'oil', 'commodity'],
        'currency': ['rupee', 'usd/inr', 'dollar', 'forex'],
        'economy': ['gdp', 'inflation', 'budget', 'fiscal', 'monetary']
    }
    
    CHANNEL_MAP = {
        'banking': ['banknifty', 'fno'],
        'it': ['nifty', 'fno'],
        'commodity': ['commodity'],
        'currency': ['currency'],
        'economy': ['education', 'nifty']
    }

    # 3. IMPACT GATE: Keywords that mean the market is moving
    HIGH_IMPACT_KEYWORDS = {
        10: ['rbi', 'repo rate', 'crash', 'plunge', 'emergency', 'default'],
        9:  ['gdp', 'inflation', 'all-time high', '52-week high', 'rate cut', 'rate hike'],
        8:  ['crude oil', 'fii selling', 'dii buying', 'rupee fall', 'earnings']
    }
    
    def __init__(self):
        self.poster = TelegramPoster()
        self.api_key = os.getenv('NEWS_API_KEY')
        
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.posted_file = self.data_dir / 'posted_news.json'
        self.daily_counter_file = self.data_dir / 'daily_post_count.json'
        
        self.posted_hashes = self.load_posted_news()
        self.daily_count = self.load_daily_count()

    def load_posted_news(self):
        if self.posted_file.exists():
            try:
                with open(self.posted_file, 'r') as f:
                    return set(json.load(f))
            except: return set()
        return set()

    def save_posted_news(self):
        with open(self.posted_file, 'w') as f:
            json.dump(list(self.posted_hashes)[-500:], f)

    def load_daily_count(self):
        today = datetime.now().strftime('%Y-%m-%d')
        if self.daily_counter_file.exists():
            try:
                with open(self.daily_counter_file, 'r') as f:
                    data = json.load(f)
                    return data.get('count', 0) if data.get('date') == today else 0
            except: return 0
        return 0

    def get_content_hash(self, title):
        # Professional hashing to prevent duplicates
        return hashlib.md5(title.lower().strip()[:100].encode()).hexdigest()

    def fetch_news(self):
        if not self.api_key: return []
        
        url = "https://newsapi.org/v2/everything"
        # Deep search for Indian Market Impact
        query = '(Nifty OR Sensex OR RBI OR "Market News" OR "Economy India") AND (Impact OR Alert OR Warning)'
        
        params = {
            'q': query,
            'domains': self.FINANCE_DOMAINS,
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.api_key,
            'pageSize': 30
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            articles = response.json().get('articles', [])
            filtered = []
            
            for art in articles:
                title = art['title']
                if not title or '[Removed]' in title: continue
                
                # Check Deduplication
                news_hash = self.get_content_hash(title)
                if news_hash in self.posted_hashes: continue
                
                # Check Freshness (Must be within 6 hours)
                pub_time = datetime.fromisoformat(art['publishedAt'].replace('Z', '+00:00'))
                if (datetime.now().astimezone() - pub_time).total_seconds() > 6 * 3600:
                    continue

                # Calculate Impact & Worthiness
                text = (title + ' ' + (art.get('description') or '')).lower()
                impact_score = 7 # Default
                for score, keywords in self.HIGH_IMPACT_KEYWORDS.items():
                    if any(kw in text for kw in keywords):
                        impact_score = score
                        break
                
                if self.daily_count < 10:
                    self.posted_hashes.add(news_hash)
                    self.daily_count += 1
                    filtered.append({
                        'title': title,
                        'description': (art.get('description') or 'Full analysis on website.')[:350],
                        'source': art['source']['name'],
                        'time': datetime.now().strftime('%H:%M IST'),
                        'impact_score': impact_score
                    })
            
            self.save_posted_news()
            with open(self.daily_counter_file, 'w') as f:
                json.dump({'date': datetime.now().strftime('%Y-%m-%d'), 'count': self.daily_count}, f)
            return filtered
        except: return []

    def post_news(self):
        items = self.fetch_news()
        if not items: return

        for item in items:
            urgency = "🔴 URGENT" if item['impact_score'] >= 9 else "🟠 IMPORTANT"
            
            # Determine Sector
            text = (item['title'] + ' ' + item['description']).lower()
            found_sectors = [s for s, kws in self.SECTOR_KEYWORDS.items() if any(k in text for k in kws)]
            sectors_str = ", ".join(found_sectors) if found_sectors else "General Economy"

            message = f"{urgency} - Market Impact\n\n📰 **OMKAR TRADE SERVICES**\n\n**{item['title']}**\n\n{item['description']}...\n\n📊 **Impact Score:** {item['impact_score']}/10\n🎯 **Sector:** {sectors_str}\n🔍 **Source:** {item['source']}\n⏰ **Time:** {item['time']}"
            
            # Post to relevant channels
            self.poster.send_message('nifty', message)
            self.poster.send_message('education', message)

if __name__ == "__main__":
    NewsAggregator().post_news()
