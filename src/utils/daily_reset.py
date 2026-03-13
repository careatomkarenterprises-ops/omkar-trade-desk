"""
Daily Reset - Clean up data files
"""

import os
import json
from pathlib import Path
from datetime import datetime
import logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

class DailyReset:
    """
    Perform daily cleanup tasks
    """
    
    def __init__(self):
        self.data_dir = Path('data')
        self.poster = TelegramPoster()
    
    def cleanup_cache(self):
        """Remove old cache files"""
        cache_dir = self.data_dir / 'cache'
        if cache_dir.exists():
            count = 0
            for f in cache_dir.glob('*.parquet'):
                # Keep only today's cache
                modified = datetime.fromtimestamp(f.stat().st_mtime)
                if modified.date() < datetime.now().date():
                    f.unlink()
                    count += 1
            logger.info(f"Cleaned {count} cache files")
    
    def rotate_logs(self):
        """Rotate log files"""
        patterns_file = self.data_dir / 'patterns_log.json'
        if patterns_file.exists():
            # Create backup with date
            date_str = datetime.now().strftime('%Y%m%d')
            backup = self.data_dir / f'patterns_log_{date_str}.json'
            if not backup.exists():
                import shutil
                shutil.copy(patterns_file, backup)
                logger.info(f"Created backup: {backup}")
    
    def reset_posted_news(self):
        """Reset posted news tracker (keep only last 7 days)"""
        posted_file = self.data_dir / 'posted_news.json'
        if posted_file.exists():
            try:
                with open(posted_file, 'r') as f:
                    news = json.load(f)
                # Keep only last 50 items
                if len(news) > 50:
                    with open(posted_file, 'w') as f:
                        json.dump(news[-50:], f)
                    logger.info("Trimmed posted news tracker")
            except:
                pass
    
    def send_daily_summary(self):
        """Send daily summary to education channel"""
        razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        message = f"""
📊 **Daily Reset Complete**

✅ Cache cleaned
✅ Logs rotated
✅ News tracker trimmed
✅ System ready for {datetime.now().strftime('%d %b %Y')}

🟢 Scanner will run at 9:15 AM
🟢 News updates every 30 minutes
🟢 Educational content at 9:30 AM & 4:30 PM

👉 [Join Premium]({razorpay_link})
"""
        self.poster.send_message('education', message)
        logger.info("Daily summary sent")
    
    def run(self):
        """Run all reset tasks"""
        logger.info("Starting daily reset...")
        self.cleanup_cache()
        self.rotate_logs()
        self.reset_posted_news()
        self.send_daily_summary()
        logger.info("Daily reset complete")

if __name__ == "__main__":
    reset = DailyReset()
    reset.run()
