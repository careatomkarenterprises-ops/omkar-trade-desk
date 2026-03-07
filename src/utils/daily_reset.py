"""
Daily Reset - Clean up data files
"""

import os  # ← THIS WAS MISSING!
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
    
    def send_daily_summary(self):
        """Send daily summary to education channel"""
        razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        message = f"""
📊 **Daily Reset Complete**

✅ Cache cleaned
✅ Logs rotated
✅ System ready for {datetime.now().strftime('%d %b %Y')}

🟢 Scanner will run at 9:15 AM

👉 [Join Premium]({razorpay_link})
"""
        self.poster.send_message('education', message)
        logger.info("Daily summary sent")
    
    def run(self):
        """Run all reset tasks"""
        logger.info("Starting daily reset...")
        self.cleanup_cache()
        self.rotate_logs()
        self.send_daily_summary()
        logger.info("Daily reset complete")

if __name__ == "__main__":
    reset = DailyReset()
    reset.run()
