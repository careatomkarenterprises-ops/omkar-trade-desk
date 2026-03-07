"""
Chart Generator - Create stock charts from real data
"""

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Generate stock charts from real market data"""
    
    def __init__(self):
        self.chart_dir = 'data/charts'
        os.makedirs(self.chart_dir, exist_ok=True)
    
    def create_volume_chart(self, symbol: str, days: int = 30) -> str:
        """
        Create a volume spike chart for a stock
        Returns path to saved chart image
        """
        try:
            # Fetch real data
            ticker = yf.Ticker(f"{symbol}.NS")
            data = ticker.history(period=f"{days}d", interval="1d")
            
            if data.empty:
                return None
            
            # Calculate volume average
            data['Volume_Avg'] = data['Volume'].rolling(window=20).mean()
            
            # Create chart
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                           gridspec_kw={'height_ratios': [3, 1]})
            
            # Price chart
            ax1.plot(data.index, data['Close'], color='blue', linewidth=2, label='Close Price')
            ax1.set_title(f'{symbol} - Volume Spike Analysis', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price (₹)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Volume chart with spike highlighting
            colors = ['red' if v > a else 'gray' for v, a in zip(data['Volume'], data['Volume_Avg'])]
            ax2.bar(data.index, data['Volume'], color=colors, alpha=0.7)
            ax2.plot(data.index, data['Volume_Avg'], color='orange', linewidth=2, 
                    linestyle='--', label='20-day Avg')
            ax2.set_ylabel('Volume', fontsize=12)
            ax2.set_xlabel('Date', fontsize=12)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save chart
            filename = f"{self.chart_dir}/{symbol}_volume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=100, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Chart saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            return None
    
    def create_candlestick_chart(self, symbol: str, days: int = 30) -> str:
        """Create candlestick chart with volume"""
        try:
            # Fetch data
            ticker = yf.Ticker(f"{symbol}.NS")
            data = ticker.history(period=f"{days}d", interval="1d")
            
            if data.empty:
                return None
            
            # Prepare data for mplfinance
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Create style
            style = mpf.make_mpf_style(
                base_mpf_style='charles',
                rc={'font.size': 10}
            )
            
            # Create chart
            filename = f"{self.chart_dir}/{symbol}_candle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            mpf.plot(
                data,
                type='candle',
                style=style,
                title=f'\n{symbol} - Candlestick Chart',
                ylabel='Price (₹)',
                ylabel_lower='Volume',
                volume=True,
                savefig=filename,
                figsize=(12, 8)
            )
            
            logger.info(f"Candlestick chart saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating candlestick chart: {e}")
            return None
