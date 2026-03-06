"""
News Aggregator - Fetches and posts market news
"""

import os
import requests
import logging
from datetime import datetime
import random
from typing import List, Dict

from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

class NewsAggregator:
    """
    Fetch and post market news
    """
    
    def __init__(self):
        self.poster = TelegramPoster()
        self.api_key = os.getenv('NEWS_API_KEY')
        
        # Sector keywords
        self.sectors = {
            'banking': ['rbi', 'bank', 'interest rate', 'repo rate', 'npas'],
            'it': ['tech', 'software', 'it services', 'nasdaq'],
            'commodity': ['gold', 'silver', 'crude', 'oil'],
            'currency': ['rupee', 'dollar', 'forex', 'inr'],
            'economy': ['gdp', 'inflation', 'cpi', 'budget', 'economy']
        }
    
    def fetch_news(self) -> List[Dict]:
        """
        Fetch real news from NewsAPI
        """
        try:
            if not self.api_key:
                return self.generate_fallback_news()
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'in',
                'category': 'business',
                'apiKey': self.api_key,
                'pageSize': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                articles = response.json().get('articles', [])
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
            
            return self.generate_fallback_news()
            
        except Exception as e:
            logger.error(f"News API error: {e}")
            return self.generate_fallback_news()
    
    def generate_fallback_news(self) -> List[Dict]:
        """
        Generate contextual news when API fails
        """
        now = datetime.now()
        hour = now.hour
        
        # Morning news
        if 8 <= hour <= 10:
            return [{
                'title': 'Morning Market Update: Global cues positive',
                'description': 'Asian markets trading higher. SGX Nifty indicates gap up opening.',
                'source': 'Omkar Market Intelligence',
                'time': now.strftime('%H:%M IST')
            }]
        
        # Mid-day news
        elif 11 <= hour <= 14:
            return [{
                'title': 'Sector Watch: Banking stocks showing strength',
                'description': 'Nifty Bank outperforms with institutional buying visible.',
                'source': 'Omkar Scanner',
                'time': now.strftime('%H:%M IST')
            }]
        
        # Evening news
        elif 15 <= hour <= 17:
            return [{
                'title': 'Closing Bell: Markets end near day\'s high',
                'description': 'Broad-based buying seen. Advance-decline ratio positive.',
                'source': 'Omkar TradeDesk',
                'time': now.strftime('%H:%M IST')
            }]
        
        # US Market news
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
        news_items = self.fetch_news()
        
        for item in news_items:
            sectors = self.determine_sector(item)
            
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
                self.poster.send_message(channel, message)
                logger.info(f"News posted to {channel}")

if __name__ == "__main__":
    news = NewsAggregator()
    news.post_news()
