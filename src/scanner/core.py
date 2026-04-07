"""
Omkar Scanner Core - Optimized Business Version
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
        print("\n🔍 OmkarScanner Initializing...")
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.poster = TelegramPoster()
        print("  └─ ✅ Scanner Ready")

    # ✅ SCORE SYSTEM
    def calculate_score(self, pattern: Dict) -> int:
        score = 0

        # Strength weight (0–50)
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
                logger.error(f"Error scanning {symbol}: {e}")

        return patterns

    # ✅ SEND CLEAN TELEGRAM MESSAGE
    def send_summary(self, patterns: List[Dict], channel: str):

        if not patterns:
            return

        message = f"""
🚀 *AI Market Scanner*

📅 {datetime.now().strftime('%d %b %Y | %H:%M')}

🔥 *Top Opportunities Today:*
"""

        for p in patterns:
            message += f"""
🎯 {p['symbol']}
Score: {p['score']}/100
Pattern: {p['primary_pattern']}
Trend: {p.get('trend','neutral').upper()}
"""

        message += """

━━━━━━━━━━━━━━━━━━
⚠️ Educational purpose only
"""

        self.poster.send_message(channel, message)

    # ✅ MAIN RUN
    def run(self):
        print("\n🚀 Running Optimized Scanner...\n")

        all_patterns = self.scan_market()

        if not all_patterns:
            print("❌ No patterns found")
            return

        # Sort by score
        sorted_patterns = sorted(all_patterns, key=lambda x: x['score'], reverse=True)

        # FREE vs PREMIUM
        top_5 = sorted_patterns[:5]
        free_2 = sorted_patterns[:2]

        # Send messages
        self.send_summary(free_2, 'education')   # FREE CHANNEL
        self.send_summary(top_5, 'premium')      # PREMIUM CHANNEL

        print(f"✅ Sent {len(top_5)} premium & {len(free_2)} free alerts")


if __name__ == "__main__":
    scanner = OmkarScanner()
    scanner.run()
