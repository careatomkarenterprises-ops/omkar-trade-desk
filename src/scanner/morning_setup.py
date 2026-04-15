import os
import json
import pyotp
from kiteconnect import KiteConnect

def get_kite_instance():
    """Provides a ready-to-use Kite connection to all agents."""
    api_key = os.getenv('ZERODHA_API_KEY')
    access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
    
    if not api_key or not access_token:
        print("❌ API Key or Access Token missing in Secrets!")
        return None
        
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite

def refresh_all_data():
    """Refreshes market tokens for the scanner logic."""
    kite = get_kite_instance()
    if not kite:
        return

    try:
        print("📥 Fetching fresh instruments from Zerodha...")
        instruments = kite.instruments("CDS")
        token_map = {f"CDS:{i['tradingsymbol']}": i['instrument_token'] for i in instruments}
        
        os.makedirs('data', exist_ok=True)
        with open('data/instrument_tokens.json', 'w') as f:
            json.dump(token_map, f)
        print("✅ Market Tokens Refreshed Successfully.")
    except Exception as e:
        print(f"❌ Data Refresh Error: {e}")

if __name__ == "__main__":
    refresh_all_data()
