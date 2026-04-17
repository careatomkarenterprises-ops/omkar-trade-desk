"""
Omkar Trade Services - F&O Agent
Logic: Institutional OI Build-up & Future Spread Analysis
"""
import pandas as pd
from datetime import datetime
from kiteconnect import KiteConnect

class FnOAgent:
    def __init__(self, kite_instance):
        self.kite = kite_instance

    def get_futures_master(self, underlying="NIFTY"):
        """Fetches Current, Next, and Far month futures for any symbol."""
        instruments = self.kite.instruments("NFO")
        df = pd.DataFrame(instruments)
        
        # Filter for the specific index/stock futures
        fut_df = df[(df['segment'] == 'NFO-FUT') & (df['name'] == underlying)]
        fut_df.loc[:, 'expiry'] = pd.to_datetime(fut_df['expiry'])
        
        # Sort by expiry to get Current (0), Next (1), and Far (2)
        fut_df = fut_df.sort_values('expiry').head(3)
        return fut_df

    def scan_institutional_build(self, symbol="NIFTY"):
        """Analyzes OI and Price to find Institutional Long/Short build-up."""
        futs = self.get_futures_master(symbol)
        results = []
        
        for index, row in futs.iterrows():
            quote = self.kite.quote(f"NFO:{row['tradingsymbol']}")[f"NFO:{row['tradingsymbol']}"]
            
            oi = quote['oi']
            price_change = quote['last_price'] - quote['ohlc']['close']
            
            # Logic for Institutional Footprint
            sentiment = "Neutral"
            if price_change > 0 and quote['oi_day_high'] > quote['oi']: sentiment = "Long Build-up"
            elif price_change < 0 and quote['oi_day_high'] > quote['oi']: sentiment = "Short Build-up"
            
            results.append({
                'expiry_type': ['Current', 'Next', 'Far'][len(results)],
                'symbol': row['tradingsymbol'],
                'price': quote['last_price'],
                'oi_change': quote['oi_day_high'],
                'sentiment': sentiment
            })
        return results
