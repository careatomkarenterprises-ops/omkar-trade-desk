from kiteconnect import KiteConnect

# =====================================
# ZERODHA API DETAILS
# =====================================

api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

# Paste request token here
request_token = "PASTE_REQUEST_TOKEN"

# =====================================
# GENERATE ACCESS TOKEN
# =====================================

kite = KiteConnect(api_key=api_key)

data = kite.generate_session(
    request_token=request_token,
    api_secret=api_secret
)

print("\n====================================")
print("✅ ACCESS TOKEN GENERATED")
print("====================================\n")

print(data["access_token"])
