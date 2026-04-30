import os
import json
import requests
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from src.telegram.poster import send_message

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class NewsAggregator:

    FINANCE_DOMAINS = (
        "moneycontrol.com,"
        "economictimes.indiatimes.com,"
        "financialexpress.com,"
        "business-standard.com,"
        "livemint.com"
    )

    # =========================
    # IMPACT ENGINE
    # =========================
    HIGH_IMPACT_KEYWORDS = {

        10: [
            'market crash',
            'stock market crash',
            'emergency',
            'default',
            'bank collapse',
            'war',
            'global recession'
        ],

        9: [
            'rbi',
            'repo rate',
            'inflation',
            'gdp',
            'rate hike',
            'rate cut',
            'all-time high',
            'all-time low',
            '52-week high',
            '52-week low'
        ],

        8: [
            'fii selling',
            'fii buying',
            'dii buying',
            'dii selling',
            'earnings',
            'profit jump',
            'profit falls',
            'crude oil',
            'rupee falls',
            'rupee weakens',
            'market rally',
            'market falls'
        ],

        7: [
            'nifty',
            'sensex',
            'banknifty',
            'breakout',
            'support',
            'resistance',
            'stock surge',
            'volume spike'
        ]
    }

    IMPORTANT_MARKET_WORDS = [
        "nifty",
        "sensex",
        "banknifty",
        "rbi",
        "inflation",
        "fii",
        "dii",
        "earnings",
        "breakout",
        "market"
    ]

    def __init__(self):

        self.api_key = os.getenv("NEWS_API_KEY")

        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self.posted_file = self.data_dir / "posted_news.json"

        self.posted_hashes = self.load_posted_news()

        logger.info("✅ News Aggregator Started")

    # =========================
    # LOAD CACHE
    # =========================
    def load_posted_news(self):

        if self.posted_file.exists():

            try:
                with open(self.posted_file, "r") as f:
                    return set(json.load(f))

            except Exception as e:
                logger.error(f"Load cache error: {e}")

        return set()

    # =========================
    # SAVE CACHE
    # =========================
    def save_posted_news(self):

        try:
            with open(self.posted_file, "w") as f:
                json.dump(list(self.posted_hashes)[-500:], f)

        except Exception as e:
            logger.error(f"Save cache error: {e}")

    # =========================
    # UNIQUE HASH
    # =========================
    def get_hash(self, text):

        return hashlib.md5(
            text.lower().strip().encode()
        ).hexdigest()

    # =========================
    # FETCH NEWS
    # =========================
    def fetch_news(self):

        if not self.api_key:

            logger.error("❌ NEWS_API_KEY missing")
            return []

        url = "https://newsapi.org/v2/everything"

        query = (
            '(Nifty OR Sensex OR RBI OR '
            '"Indian Stock Market" OR '
            '"Economy India")'
        )

        params = {
            "q": query,
            "domains": self.FINANCE_DOMAINS,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": self.api_key,
            "pageSize": 20
        }

        try:

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            data = response.json()

            if data.get("status") != "ok":

                logger.error(
                    f"❌ API Error: {data.get('message')}"
                )

                return []

            articles = data.get("articles", [])

            logger.info(
                f"✅ Raw articles fetched: {len(articles)}"
            )

            filtered = []

            for art in articles:

                title = art.get("title", "")

                if not title:
                    continue

                if "[Removed]" in title:
                    continue

                news_hash = self.get_hash(title)

                # DUPLICATE CHECK
                if news_hash in self.posted_hashes:
                    continue

                description = art.get("description") or ""

                text = (
                    title + " " + description
                ).lower()

                # =========================
                # IMPACT SCORE ENGINE
                # =========================
                impact_score = 5

                for score, keywords in self.HIGH_IMPACT_KEYWORDS.items():

                    if any(
                        kw.lower() in text
                        for kw in keywords
                    ):
                        impact_score = score
                        break

                # =========================
                # STRICT FILTERING
                # =========================
                if impact_score < 8:

                    if not any(
                        word in text
                        for word in self.IMPORTANT_MARKET_WORDS
                    ):
                        continue

                # =========================
                # SAVE HASH
                # =========================
                self.posted_hashes.add(news_hash)

                filtered.append({
                    "title": title,
                    "description": description[:250],
                    "source": art["source"]["name"],
                    "impact_score": impact_score
                })

                logger.info(
                    f"📰 Important News Added "
                    f"(Score {impact_score})"
                )

            self.save_posted_news()

            return filtered

        except Exception as e:

            logger.error(f"❌ Fetch error: {e}")

            return []

    # =========================
    # POST TO TELEGRAM
    # =========================
    def post_news(self):

        logger.info("🚀 Starting News Engine")

        news_items = self.fetch_news()

        if not news_items:

            logger.info("📭 No important news found")
            return

        logger.info(
            f"📨 Posting {len(news_items)} important news"
        )

        for i, item in enumerate(news_items):

            urgency = (
                "🔴 URGENT"
                if item["impact_score"] >= 9
                else "🟠 IMPORTANT"
            )

            message = (
                f"{urgency} - MARKET UPDATE\n\n"
                f"📰 *{item['title']}*\n\n"
                f"{item['description']}\n\n"
                f"📊 Impact Score: "
                f"{item['impact_score']}/10\n"
                f"📰 Source: {item['source']}\n\n"
                f"⚠️ Educational purpose only"
            )

            try:

                send_message("free_main", message)
                send_message("premium", message)

                logger.info(
                    f"✅ Posted news "
                    f"{i+1}/{len(news_items)}"
                )

            except Exception as e:

                logger.error(
                    f"❌ Telegram post failed: {e}"
                )

        logger.info("🎉 News posting completed")


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    logger.info("=" * 50)
    logger.info("📰 NEWS ENGINE STARTED")
    logger.info("=" * 50)

    aggregator = NewsAggregator()

    aggregator.post_news()

    logger.info("=" * 50)
