import os
import json
import requests
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from src.telegram.poster import send_message

# ============================================
# LOGGING
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class NewsAggregator:

    # ============================================
    # TRUSTED FINANCIAL SOURCES
    # ============================================
    FINANCE_DOMAINS = (
        "moneycontrol.com,"
        "economictimes.indiatimes.com,"
        "financialexpress.com,"
        "business-standard.com,"
        "livemint.com"
    )

    # ============================================
    # HIGH IMPACT KEYWORDS
    # ============================================
    HIGH_IMPACT_KEYWORDS = {

        10: [
            'rbi',
            'repo rate',
            'emergency',
            'market crash',
            'plunge',
            'default',
            'bank crisis',
            'war',
            'fed rate',
            'recession'
        ],

        9: [
            'inflation',
            'gdp',
            'rate cut',
            'rate hike',
            'all-time high',
            '52-week high',
            'fii selling',
            'fii buying',
            'dii buying',
            'dii selling'
        ],

        8: [
            'crude oil',
            'earnings',
            'profit jump',
            'profit fall',
            'breakout',
            'nifty',
            'sensex',
            'banknifty'
        ]
    }

    # ============================================
    # INIT
    # ============================================
    def __init__(self):

        self.api_key = os.getenv("NEWS_API_KEY")

        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self.posted_file = self.data_dir / "posted_news.json"

        self.posted_hashes = self._load_posted_news()

        logger.info("✅ News Aggregator Started")

    # ============================================
    # LOAD OLD POSTS
    # ============================================
    def _load_posted_news(self):

        if self.posted_file.exists():

            try:
                with open(self.posted_file, "r") as f:
                    return set(json.load(f))

            except Exception as e:
                logger.error(f"Load error: {e}")

        return set()

    # ============================================
    # SAVE POSTED HASHES
    # ============================================
    def _save_posted_news(self):

        try:
            with open(self.posted_file, "w") as f:
                json.dump(list(self.posted_hashes)[-500:], f)

        except Exception as e:
            logger.error(f"Save error: {e}")

    # ============================================
    # UNIQUE HASH
    # ============================================
    def _get_hash(self, text):

        return hashlib.md5(
            text.lower().strip()[:120].encode()
        ).hexdigest()

    # ============================================
    # FETCH NEWS
    # ============================================
    def fetch_news(self):

        if not self.api_key:
            logger.error("❌ NEWS_API_KEY missing")
            return []

        url = "https://newsapi.org/v2/everything"

        params = {
            "q": (
                'Nifty OR Sensex OR RBI OR '
                'Inflation OR GDP OR Market'
            ),
            "domains": self.FINANCE_DOMAINS,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20,
            "apiKey": self.api_key
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
                    f"❌ NewsAPI Error: "
                    f"{data.get('message')}"
                )

                return []

            articles = data.get("articles", [])

            logger.info(
                f"✅ Raw articles fetched: "
                f"{len(articles)}"
            )

            filtered = []

            for art in articles:

                title = art.get("title", "")

                if not title:
                    continue

                if "[Removed]" in title:
                    continue

                # ============================================
                # DUPLICATE CHECK
                # ============================================
                news_hash = self._get_hash(title)

                if news_hash in self.posted_hashes:
                    continue

                # ============================================
                # AGE FILTER
                # ============================================
                try:

                    pub_time = datetime.fromisoformat(
                        art["publishedAt"].replace("Z", "+00:00")
                    )

                    age_seconds = (
                        datetime.now().astimezone() - pub_time
                    ).total_seconds()

                    # older than 6 hours ignore
                    if age_seconds > 21600:
                        continue

                except:
                    continue

                # ============================================
                # IMPACT SCORE
                # ============================================
                text = (
                    title + " " +
                    (art.get("description") or "")
                ).lower()

                impact_score = 5

                for score, keywords in (
                    self.HIGH_IMPACT_KEYWORDS.items()
                ):

                    if any(
                        keyword in text
                        for keyword in keywords
                    ):
                        impact_score = score
                        break

                # ============================================
                # IGNORE LOW IMPACT
                # ============================================
                if impact_score < 8:
                    continue

                # ============================================
                # SAVE
                # ============================================
                self.posted_hashes.add(news_hash)

                filtered.append({

                    "title": title,

                    "description": (
                        art.get("description")
                        or "Market update"
                    )[:250],

                    "source": (
                        art.get("source", {})
                        .get("name", "Unknown")
                    ),

                    "impact_score": impact_score
                })

            self._save_posted_news()

            # ============================================
            # SORT BY IMPACT
            # ============================================
            filtered = sorted(
                filtered,
                key=lambda x: x["impact_score"],
                reverse=True
            )

            # ============================================
            # LIMIT POSTS
            # ============================================
            return filtered[:5]

        except Exception as e:

            logger.error(f"❌ Fetch error: {e}")

            return []

    # ============================================
    # POST NEWS
    # ============================================
    def post_news(self):

        logger.info("🚀 Starting News Engine")

        items = self.fetch_news()

        if not items:

            logger.info("📭 No important news found")

            return

        logger.info(
            f"📨 Posting {len(items)} "
            f"important news alerts"
        )

        for idx, item in enumerate(items, start=1):

            urgency = (
                "🔴 URGENT"
                if item["impact_score"] >= 9
                else "🟠 IMPORTANT"
            )

            message = (

                f"{urgency} - MARKET ALERT\n\n"

                f"📰 *{item['title']}*\n\n"

                f"{item['description']}\n\n"

                f"📊 Impact Score: "
                f"{item['impact_score']}/10\n"

                f"📰 Source: "
                f"{item['source']}\n\n"

                f"⚠️ Educational purpose only"
            )

            # ============================================
            # SEND CHANNELS
            # ============================================
            channels = [
                "free_main",
                "free_signals",
                "premium",
                "premium_elite"
            ]

            for channel in channels:

                try:

                    send_message(channel, message)

                    logger.info(
                        f"✅ Sent to {channel}"
                    )

                except Exception as e:

                    logger.error(
                        f"❌ Failed {channel}: {e}"
                    )

            logger.info(
                f"✅ Posted news "
                f"{idx}/{len(items)}"
            )

        logger.info("🎉 News posting completed")


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":

    logger.info("=" * 50)

    logger.info("📰 NEWS ENGINE STARTED")

    logger.info("=" * 50)

    aggregator = NewsAggregator()

    aggregator.post_news()

    logger.info("=" * 50)
