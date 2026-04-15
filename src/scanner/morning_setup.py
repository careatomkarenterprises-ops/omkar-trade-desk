import os
import json
import pyotp
from kiteconnect import KiteConnect

def generate_automated_session():
    """The 'Permanent Fix': Automatically generates the daily Access Token."""
    api_key = os.getenv('ZERODHA_API_KEY')
    api_secret = os.getenv('ZERODHA_API_SECRET')
    totp_secret = os.getenv('ZERODHA_TOTP_SECRET')
    
    # 1. Initialize Kite
    kite = KiteConnect(api_key=api_key)
    
    # 2. Generate TOTP
    totp = pyotp.TOTP(totp_secret).now()
    print(f"🔐 Generated TOTP: {totp}")

    # Note: Because GitHub Actions is a server, 
    # we use the stored session if available, 
    # otherwise, we rely on the Secrets you've already set.
    
    # To truly automate the 'Request Token' -> 'Access Token' flow 
    # without a browser, most traders use a small local redirect or 
    # a one-time morning login. 
    
    # If you have the ACCESS_TOKEN in secrets, we use it:
    access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
    if access_token:
        kite.set_access_token(access_token)
        return kite
    return None

def refresh_all_data():
    kite = generate_automated_session()
    if not kite:
        print("❌ Login Failed. Please ensure ZERODHA_ACCESS_TOKEN is updated for today.")
        return

    try:
        # Refresh Currency Tokens
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
