import os
import json
import requests
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from src.telegram.poster import send_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAggregator:
    FINANCE_DOMAINS = "moneycontrol.com,economictimes.indiatimes.com,financialexpress.com,business-standard.com,livemint.com"

    HIGH_IMPACT_KEYWORDS = {
        10: ['rbi', 'repo rate', 'crash', 'plunge', 'emergency', 'default'],
        9: ['gdp', 'inflation', 'all-time high', '52-week high', 'rate cut', 'rate hike'],
        8: ['crude oil', 'fii selling', 'dii buying', 'rupee fall', 'earnings']
    }

    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.posted_file = self.data_dir / 'posted_news.json'
        self.posted_hashes = self._load_posted_news()

    def _load_posted_news(self):
        if self.posted_file.exists():
            try:
                with open(self.posted_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def _save_posted_news(self):
        with open(self.posted_file, 'w') as f:
            json.dump(list(self.posted_hashes)[-500:], f)

    def _get_content_hash(self, title):
        return hashlib.md5(title.lower().strip()[:100].encode()).hexdigest()

    def fetch_news(self):
        if not self.api_key:
            logger.error("No NEWS_API_KEY found")
            return []

        url = "https://newsapi.org/v2/everything"
        query = '(Nifty OR Sensex OR RBI OR "Market News" OR "Economy India")'

        params = {
            'q': query,
            'domains': self.FINANCE_DOMAINS,
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.api_key,
            'pageSize': 20
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            if data.get('status') != 'ok':
                logger.error(f"NewsAPI error: {data.get('message')}")
                return []

            articles = data.get('articles', [])
            logger.info(f"Fetched {len(articles)} articles")

            filtered = []
            for art in articles:
                title = art['title']
                if not title or '[Removed]' in title:
                    continue

                news_hash = self._get_content_hash(title)
                if news_hash in self.posted_hashes:
                    continue

                pub_time = datetime.fromisoformat(art['publishedAt'].replace('Z', '+00:00'))
                if (datetime.now().astimezone() - pub_time).total_seconds() > 6 * 3600:
                    continue

                text = (title + ' ' + (art.get('description') or '')).lower()
                impact_score = 7
                for score, keywords in self.HIGH_IMPACT_KEYWORDS.items():
                    if any(kw in text for kw in keywords):
                        impact_score = score
                        break

                self.posted_hashes.add(news_hash)
                filtered.append({
                    'title': title,
                    'description': (art.get('description') or 'Full analysis on website.')[:350],
                    'source': art['source']['name'],
                    'impact_score': impact_score
                })

            self._save_posted_news()
            logger.info(f"Filtered {len(filtered)} new news items")
            return filtered
        except Exception as e:
            logger.error(f"News fetch error: {e}")
            return []

    def post_news(self):
        items = self.fetch_news()
        if not items:
            logger.info("No news items to post")
            return

        for item in items:
            urgency = "🔴 URGENT" if item['impact_score'] >= 9 else "🟠 IMPORTANT"
            message = (f"{urgency} - Market Impact\n\n"
                       f"📰 **{item['title']}**\n\n"
                       f"{item['description']}...\n\n"
                       f"📊 **Impact Score:** {item['impact_score']}/10\n"
                       f"🔍 **Source:** {item['source']}\n"
                       f"⚠️ Educational purpose only.")

            send_message("free_signals", message)
            send_message("premium", message)
            send_message("premium_elite", message)
            logger.info(f"Posted news: {item['title'][:50]}...")

if __name__ == "__main__":
    NewsAggregator().post_news()
