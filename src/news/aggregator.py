import os
import json
import requests
import hashlib
import logging
from datetime import datetime
from pathlib import Path

# ============================
# LOGGING
# ============================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ============================
# NEWS AGGREGATOR
# ============================

class NewsAggregator:

    FINANCE_DOMAINS = (
        "moneycontrol.com,"
        "economictimes.indiatimes.com,"
        "financialexpress.com,"
        "business-standard.com,"
        "livemint.com"
    )

    HIGH_IMPACT_KEYWORDS = {
        10: ['rbi', 'repo rate', 'crash', 'plunge', 'emergency', 'default'],
        9: ['gdp', 'inflation', 'all-time high', '52-week high', 'rate cut', 'rate hike'],
        8: ['crude oil', 'fii selling', 'dii buying', 'rupee fall', 'earnings']
    }

    # ============================
    # INIT
    # ============================

    def __init__(self):

        self.api_key = os.getenv("NEWS_API_KEY")

        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        self.channels = [
            os.getenv("CHANNEL_FREE"),
            os.getenv("CHANNEL_EDUCATION"),
            os.getenv("CHANNEL_PREMIUM"),
            os.getenv("CHANNEL_INTRADAY")
        ]

        # remove empty channels
        self.channels = [c for c in self.channels if c]

        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self.posted_file = self.data_dir / "posted_news.json"

        self.posted_hashes = self._load_posted_news()

        logger.info("✅ News Aggregator initialized")

    # ============================
    # LOAD POSTED NEWS
    # ============================

    def _load_posted_news(self):

        if self.posted_file.exists():

            try:

                with open(self.posted_file, "r") as f:

                    data = json.load(f)

                    logger.info(f"✅ Loaded {len(data)} old news hashes")

                    return set(data)

            except Exception as e:

                logger.error(f"❌ Load error: {e}")

        return set()

    # ============================
    # SAVE POSTED NEWS
    # ============================

    def _save_posted_news(self):

        try:

            with open(self.posted_file, "w") as f:

                json.dump(list(self.posted_hashes)[-500:], f)

            logger.info("✅ Posted news cache saved")

        except Exception as e:

            logger.error(f"❌ Save error: {e}")

    # ============================
    # HASH
    # ============================

    def _get_content_hash(self, title):

        return hashlib.md5(
            title.lower().strip()[:100].encode()
        ).hexdigest()

    # ============================
    # FETCH NEWS
    # ============================

    def fetch_news(self):

        if not self.api_key:

            logger.error("❌ NEWS_API_KEY missing")

            return []

        logger.info("📡 Fetching market news")

        url = "https://newsapi.org/v2/everything"

        query = (
            '(Nifty OR Sensex OR RBI OR '
            '"Market News" OR "Indian Economy")'
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
                timeout=20
            )

            data = response.json()

            if data.get("status") != "ok":

                logger.error(
                    f"❌ NewsAPI error: {data.get('message')}"
                )

                return []

            articles = data.get("articles", [])

            logger.info(f"✅ Raw articles fetched: {len(articles)}")

            filtered = []

            for art in articles:

                title = art.get("title", "")

                if not title:
                    continue

                if "[Removed]" in title:
                    continue

                news_hash = self._get_content_hash(title)

                if news_hash in self.posted_hashes:
                    continue

                text = (
                    title + " " +
                    (art.get("description") or "")
                ).lower()

                impact_score = 7

                for score, keywords in self.HIGH_IMPACT_KEYWORDS.items():

                    if any(k in text for k in keywords):

                        impact_score = score

                        break

                self.posted_hashes.add(news_hash)

                filtered.append({
                    "title": title,
                    "description": (
                        art.get("description")
                        or "Read full report online."
                    )[:300],
                    "source": art["source"]["name"],
                    "impact_score": impact_score
                })

            self._save_posted_news()

            logger.info(
                f"✅ Final filtered news: {len(filtered)}"
            )

            return filtered

        except Exception as e:

            logger.error(f"❌ Fetch error: {e}")

            return []

    # ============================
    # SEND TELEGRAM
    # ============================

    def send_telegram(self, channel, message):

        try:

            url = (
                f"https://api.telegram.org/bot"
                f"{self.bot_token}/sendMessage"
            )

            payload = {
                "chat_id": channel,
                "text": message,
                "parse_mode": "HTML"
            }

            response = requests.post(
                url,
                data=payload,
                timeout=20
            )

            logger.info(
                f"✅ Sent to {channel} "
                f"| Status {response.status_code}"
            )

        except Exception as e:

            logger.error(f"❌ Telegram error: {e}")

    # ============================
    # POST NEWS
    # ============================

    def post_news(self):

        logger.info("🚀 Starting news engine")

        items = self.fetch_news()

        if not items:

            logger.info("📭 No fresh news found")

            return

        logger.info(
            f"📨 Posting {len(items)} news items"
        )

        for i, item in enumerate(items):

            urgency = (
                "🔴 URGENT"
                if item["impact_score"] >= 9
                else "🟠 IMPORTANT"
            )

            message = (
                f"{urgency} - Market Impact\n\n"
                f"📰 <b>{item['title']}</b>\n\n"
                f"{item['description']}\n\n"
                f"📊 Impact Score: "
                f"{item['impact_score']}/10\n"
                f"🔍 Source: {item['source']}\n\n"
                f"⚠️ Educational purpose only"
            )

            for channel in self.channels:

                self.send_telegram(channel, message)

            logger.info(
                f"✅ Posted news "
                f"{i+1}/{len(items)}"
            )

        logger.info("🎉 News posting completed")

# ============================
# MAIN
# ============================

if __name__ == "__main__":

    logger.info("=" * 50)

    logger.info("📰 NEWS AGGREGATOR STARTED")

    logger.info("=" * 50)

    aggregator = NewsAggregator()

    aggregator.post_news()

    logger.info("=" * 50)
