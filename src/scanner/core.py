"""
Omkar Scanner Core - Business Optimized Version
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

class OmkarScanner:

    def __init__(self):
        print("\n🔍 Initializing Omkar Scanner...")
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.poster = TelegramPoster()
        print("✅ System Ready\n")

    # ✅ SCORING SYSTEM
    def calculate_score(self, pattern: Dict) -> int:
        score = 0

        # Strength weight (max 50)
        score += pattern.get('strength', 0) * 50

        # Volume boost
        if pattern.get('volume_ratio', 1) > 2:
            score += 20

        # Trend boost
        if pattern.get('trend') == 'bullish':
            score += 15

        return min(100, int(score))

    # ✅ SCAN MARKET
    def scan_market(self) -> List[Dict]:
        patterns = []

        for symbol in self.fetcher.nifty_stocks.keys():
            try:
                data = self.fetcher.get_stock_data(symbol)

                if data:
                    pattern = self.detector.analyze(symbol, data)

                    if pattern and pattern.get('has_pattern'):
                        pattern['score'] = self.calculate_score(pattern)
                        patterns.append(pattern)

            except Exception as e:
                logger.error(f"{symbol} error: {e}")

        return patterns

    # ✅ CLEAN TELEGRAM OUTPUT
    def send_summary(self, patterns: List[Dict], channel: str):

        if not patterns:
            return

        message = f"""
🚀 *AI Market Intelligence Scanner*

📅 {datetime.now().strftime('%d %b %Y | %H:%M')}

🔥 *Top High-Momentum Candidates:*
"""

        for p in patterns:
            message += f"""
🎯 {p['symbol']}
Score: {p['score']}/100
Insight: {p['primary_pattern']}
Trend: {p.get('trend','neutral').upper()}
Volume: {p.get('volume_ratio',1)}x
"""

        message += """

━━━━━━━━━━━━━━━━━━
⚠️ Educational insights only
"""

        self.poster.send_message(channel, message)

    # ✅ MAIN EXECUTION
    def run(self):
        print("🚀 Running Scanner...\n")

        patterns = self.scan_market()

        if not patterns:
            print("❌ No patterns found")
            return

        # Sort by score
        patterns_sorted = sorted(patterns, key=lambda x: x['score'], reverse=True)

        # Free vs Premium
        free_patterns = patterns_sorted[:2]
        premium_patterns = patterns_sorted[:5]

        # Send outputs
        self.send_summary(free_patterns, 'education')
        self.send_summary(premium_patterns, 'premium')

        print(f"✅ Sent {len(free_patterns)} FREE & {len(premium_patterns)} PREMIUM alerts\n")


if __name__ == "__main__":
    scanner = OmkarScanner()
    scanner.run()
