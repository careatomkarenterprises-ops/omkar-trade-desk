import os
import sys
import requests
import pytz
from datetime import datetime

# =====================================================================
# SYSTEM DIAGNOSTICS LAYER
# =====================================================================
def run_diagnostics():
    print("=====================================================")
    print("🚀 INITIALIZING OMKAR SYSTEM ENVIRONMENT DISPATCH")
    print("=====================================================")
    
    errors_found = False

    # 1. Verify System Clock and Timezones
    try:
        ist = pytz.timezone('Asia/Kolkata')
        time_now = datetime.now(ist)
        print(f"📅 System Clock Sync (IST): {time_now.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"❌ Timezone Guard Failure: {e}")
        errors_found = True

    print("\n--- 🔐 REPOSITORY ENVIRONMENT SECRETS CHECK ---")
    
    # 2. Check Environment Variables Safely Without Leaking Data
    required_secrets = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "CHANNEL_FREE_MAIN": os.getenv("CHANNEL_FREE_MAIN"),
        "KITE_API_KEY": os.getenv("KITE_API_KEY"),
        "KITE_ACCESS_TOKEN": os.getenv("KITE_ACCESS_TOKEN")
    }

    for secret_name, secret_val in required_secrets.items():
        if not secret_val:
            print(f"❌ CRITICAL SECRET MISSING: {secret_name} is not set in GitHub Settings!")
            errors_found = True
        else:
            # Mask the token for safety, showing only the length characteristics
            masked = secret_val[:4] + "..." + secret_val[-4:] if len(secret_val) > 8 else "Configured"
            print(f"✅ {secret_name}: Verified Loaded ({masked})")

    print("\n--- 🏦 BROKER CONNECTIVITY GATEWAY CHECK ---")

    # 3. Test Zerodha API Status directly using standard network layer
    if required_secrets["KITE_API_KEY"] and required_secrets["KITE_ACCESS_TOKEN"]:
        try:
            # Low-level headers verification check to bypass rigid module limits
            url = "https://api.kite.trade/user/profile"
            headers = {
                "X-Kite-Version": "3",
                "Authorization": f"token {required_secrets['KITE_API_KEY']}:{required_secrets['KITE_ACCESS_TOKEN']}"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json().get("data", {})
                print(f"✅ Zerodha API Handshake: SUCCESS")
                print(f"👤 Account Holder: {user_data.get('user_name', 'Unknown User')} ({user_data.get('user_id', 'N/A')})")
            else:
                print(f"❌ Zerodha API Handshake: FAILED (HTTP Status {response.status_code})")
                print(f"📝 API Server Response: {response.text}")
                errors_found = True
        except Exception as e:
            print(f"❌ Network Gateway Exception while targeting Zerodha: {e}")
            errors_found = True
    else:
        print("⚠️ Skipping Broker API test due to missing credentials.")
        errors_found = True

    print("\n--- 📁 CORE ASSETS STRUCTURAL VERIFICATION ---")

    # 4. Check for critical infrastructure files
    if os.path.exists("fno_stocks.csv"):
        print("✅ Core Asset Located: 'fno_stocks.csv' found in root tree.")
        try:
            with open("fno_stocks.csv", "r") as f:
                lines = [f.readline().strip() for _ in range(5)]
            print(f"📄 Top Data Lines Preview: {lines}")
        except Exception as e:
            print(f"⚠️ Unable to parse content preview within 'fno_stocks.csv': {e}")
    else:
        print("❌ CRITICAL FILE MISSING: 'fno_stocks.csv' cannot be found in the root directory!")
        errors_found = True

    print("=====================================================")
    if errors_found:
        print("💥 ENVIRONMENT DIAGNOSTIC RESULT: FAILURE (See logs above)")
        print("=====================================================")
        sys.exit(1) # Gracefully signal a hard failure to GitHub Actions interface
    else:
        print("🎉 ENVIRONMENT DIAGNOSTIC RESULT: ALL CORES OPERATIONAL")
        print("=====================================================")

if __name__ == "__main__":
    run_diagnostics()
