import os
import random
import logging
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import pandas as pd

from src.telegram.poster import TelegramPoster
from src.scanner.zerodha_fetcher import ZerodhaFetcher

logger = logging.getLogger(__name__)

class MarketingContent:
    def __init__(self):
        print("\n" + "="*60)
        print("📢 OMKAR MARKETING INITIALIZATION")
        print("="*60)
        
        self.poster = TelegramPoster()
        self.fetcher = ZerodhaFetcher()
        self.razorpay_link = os.getenv('RAZORPAY_LINK', 'https://rzp.io/l/omkar_pro')
        
        # Load F&O stocks
        self.stock_list = self.load_stock_list()
        
        self.lesson_templates = [
            {
                "name": "volume",
                "content": "📚 **TODAY'S LESSON: Volume Spike**\n\n**EXAMPLE: {symbol}** {data_source_badge}\n\n📊 **Data:**\n• Price: ₹{price}\n• Volume: {volume_ratio}x Avg\n\n🔍 **Insight:**\n{key_insight}\n\n👉 [Join Elite Channel]({self.razorpay_link})"
            },
            {
                "name": "trend",
                "content": "📈 **TREND ANALYSIS: {symbol}** {data_source_badge}\n\n📊 **Trend:** {trend}\n📊 **Strength:** {strength}/10\n\n💡 **Observation:** {observation}\n\n🚀 [Get Live Signals Here]({self.razorpay_link})"
            }
        ]

    def load_stock_list(self):
        stock_file = Path('data/fno_stocks.csv')
        if stock_file.exists():
            try:
                df = pd.read_csv(stock_file)
                return df['symbol'].tolist()
            except:
                pass
        return ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'SBIN', 'ITC']

    def calculate_rsi(self, data: pd.DataFrame) -> float:
        try:
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            return round(rsi.iloc[-1], 1)
        except:
            return 50.0

    def get_market_example(self) -> Optional[Dict]:
        random.shuffle(self.stock_list)
        for symbol in self.stock_list[:10]: # Check first 10 for efficiency
            data = self.fetcher.get_stock_data(symbol)
            if data is not None and not data.empty:
                current = data['Close'].iloc[-1]
                vol_ratio = data['Volume'].iloc[-1] / data['Volume'].iloc[-20:].mean()
                rsi = self.calculate_rsi(data)
                
                return {
                    'symbol': symbol,
                    'price': round(current, 2),
                    'volume_ratio': round(vol_ratio, 1),
                    'trend': "BULLISH" if current > data['Close'].rolling(20).mean().iloc[-1] else "BEARISH",
                    'strength': 8 if rsi > 60 or rsi < 40 else 5,
                    'observation': "Institutional footprint detected." if vol_ratio > 1.5 else "Stable trend.",
                    'key_insight': "High volume confirms institutional entry.",
                    'data_source_badge': "🔵 [Zerodha Live]",
                    'date': datetime.now().strftime('%d %b %Y')
                }
        return None

    def post_educational(self):
        example = self.get_market_example()
        if example:
            template = random.choice(self.lesson_templates)
            message = template['content'].format(self=self, **example)
            self.poster.send_message('education', message)
            print(f"✅ Posted {example['symbol']} to Education")

    def post_promotion(self):
        msg = f"🚀 **Boost Your Trading Performance**\n\nStop guessing! Get professional VSA alerts.\n\n🔗 [Join Premium]({self.razorpay_link})"
        self.poster.send_message('education', msg)
        print("✅ Posted Promotion")

    def run(self):
        hour = datetime.now().hour
        # Schedule Logic
        if hour in [9, 10, 16]:
            self.post_educational()
        elif hour in [11, 14, 17]:
            self.post_promotion()
        else:
            # For testing manually
            self.post_educational()

if __name__ == "__main__":
    MarketingContent().run()
