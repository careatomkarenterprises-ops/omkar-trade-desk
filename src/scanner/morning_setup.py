"""
Omkar Trade Services - Morning Token Setup
Run at 08:45 AM IST daily to refresh instrument tokens.
"""
import os
import json
import pandas as pd
from pathlib import Path
from kiteconnect import KiteConnect

def run_morning_setup(kite):
    print("🌅 Starting Omkar Morning Setup...")
    
    # 1. Fetch all instruments from Zerodha
    instruments = kite.instruments()
    df = pd.DataFrame(instruments)
    
    # 2. Filter for your specific segments
    # - Equity for Swing Trading
    # - NFO for Futures & Options
    # - CDS for Currency
    # - MCX for Commodities
    
    # Create a mapping for easy lookup: 'NSE:RELIANCE' -> 738561
    token_map = {}
    
    # Map Equity (NSE)
    nse_df = df[df['exchange'] == 'NSE']
    for _, row in nse_df.iterrows():
        token_map[f"NSE:{row['tradingsymbol']}"] = row['instrument_token']
        
    # Map F&O (NFO) - Focusing on Current/Next/Far Futures
    nfo_df = df[df['exchange'] == 'NFO']
    for _, row in nfo_df.iterrows():
        token_map[f"NFO:{row['tradingsymbol']}"] = row['instrument_token']

    # Map Currency (CDS)
    cds_df = df[df['exchange'] == 'CDS']
    for _, row in cds_df.iterrows():
        token_map[f"CDS:{row['tradingsymbol']}"] = row['instrument_token']

    # 3. Save to data folder for the scanners to use
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    with open(data_dir / 'instrument_tokens.json', 'w') as f:
        json.dump(token_map, f)
        
    print(f"✅ Successfully mapped {len(token_map)} instruments for today's session.")

if __name__ == "__main__":
    # This assumes you have your kite initialization logic ready
    # from src.auth.kite_setup import get_kite_instance
    # kite = get_kite_instance()
    # run_morning_setup(kite)
    pass
