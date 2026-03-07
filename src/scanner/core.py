"""
Omkar Scanner Core - Main Scanner Engine
Runs on GitHub Actions - No manual intervention needed
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scanner.data_fetcher import DataFetcher
from src.scanner.patterns import PatternDetector
from src.telegram.poster import TelegramPoster
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger('scanner')

class OmkarScanner:
    """
    Main scanner class - Runs completely automated
    """
    
    def __init__(self):
        # Initialize components
        self.fetcher = DataFetcher()
        self.detector = PatternDetector()
        self.poster = TelegramPoster()
        
        # Data storage
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.patterns_log = self.data_dir / 'patterns_log.json'
        
        # Load existing patterns log
        self.load_patterns_log()
        
        logger.info("Omkar Scanner initialized - Ready for auto mode")
    
    def load_patterns_log(self):
    """Load patterns from previous runs with error handling"""
    if self.patterns_log.exists():
        try:
            with open(self.patterns_log, 'r') as f:
                content = f.read().strip()
                if content:  # If file has content
                    self.patterns_history = json.loads(content)
                else:  # If file is empty
                    self.patterns_history = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'patterns': []
                    }
        except json.JSONDecodeError:
            # If JSON is corrupted, create new
            print("⚠️ Patterns log corrupted, creating new one")
            self.patterns_history = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'patterns': []
            }
    else:
        self.patterns_history = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'patterns': []
        }
        
    def scan_indices(self) -> List[Dict]:
        """Scan indices for patterns"""
        patterns_found = []
        indices = ['NIFTY 50', 'BANK NIFTY']
        
        for idx in indices:
            try:
                data = self.fetcher.get_index_data(idx)
                if data is not None:
                    pattern = self.detector.analyze(idx, data)
                    if pattern:
                        patterns_found.append(pattern)
                        channel = 'nifty' if 'NIFTY' in idx else 'banknifty'
                        self.poster.post_pattern(channel, pattern)
            except Exception as e:
                logger.error(f"Error scanning {idx}: {e}")
        
        return patterns_found
    
    def scan_commodities(self) -> List[Dict]:
        """Scan commodities for patterns"""
        patterns_found = []
        commodities = ['GOLD', 'SILVER', 'CRUDEOIL']
        
        for comm in commodities:
            try:
                data = self.fetcher.get_commodity_data(comm)
                if data is not None:
                    pattern = self.detector.analyze(comm, data)
                    if pattern:
                        patterns_found.append(pattern)
                        self.poster.post_pattern('commodity', pattern)
            except Exception as e:
                logger.error(f"Error scanning {comm}: {e}")
        
        return patterns_found
    
    def get_channel_for_stock(self, symbol: str) -> str:
        """Determine which channel gets this stock"""
        banking = ['HDFCBANK', 'ICICIBANK', 'SBIN', 'AXISBANK', 'KOTAKBANK']
        it_stocks = ['TCS', 'INFY', 'HCLTECH', 'WIPRO', 'TECHM']
        
        if symbol in banking:
            return 'banknifty'
        elif symbol in it_stocks:
            return 'nifty'
        else:
            return 'swing'
    
    def run(self):
        """Main execution function"""
        logger.info("=" * 60)
        logger.info(f"Starting scanner run at {datetime.now()}")
        logger.info("=" * 60)
        
        all_patterns = []
        
        # Run all scans
        logger.info("\n📊 Scanning Nifty stocks...")
        stock_patterns = self.scan_nifty_stocks()
        all_patterns.extend(stock_patterns)
        
        logger.info(f"\n📈 Found {len(stock_patterns)} stock patterns")
        
        logger.info("\n📉 Scanning indices...")
        index_patterns = self.scan_indices()
        all_patterns.extend(index_patterns)
        
        logger.info(f"\n🪙 Scanning commodities...")
        commodity_patterns = self.scan_commodities()
        all_patterns.extend(commodity_patterns)
        
        # Log summary
        logger.info("=" * 60)
        logger.info(f"SCAN COMPLETE - Total patterns: {len(all_patterns)}")
        logger.info("=" * 60)
        
        # Save to history
        self.patterns_history['patterns'].extend(all_patterns)
        
        # Keep only last 100 patterns
        if len(self.patterns_history['patterns']) > 100:
            self.patterns_history['patterns'] = self.patterns_history['patterns'][-100:]
        
        self.save_patterns_log()
        
        # Send summary to education channel
        if all_patterns:
            summary = f"""
📊 **Scanner Summary - {datetime.now().strftime('%d %b %Y, %H:%M')}**

🔍 Total patterns detected: {len(all_patterns)}

Top patterns:
"""
            for p in all_patterns[:3]:
                summary += f"• {p['symbol']}: {p['primary_pattern']} ({p['strength']*100:.0f}%)\n"
            
            summary += "\n👉 Full access: omkar.in/scanner"
            
            self.poster.send_message('education', summary)

if __name__ == "__main__":
    scanner = OmkarScanner()
    scanner.run()
