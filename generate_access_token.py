from kiteconnect import KiteConnect

# =====================================
# ZERODHA API DETAILS
# =====================================

api_key = "y9td8bzzuoobxp2b"
api_secret = "wqk99q83t3zcufo0m354bzpegl57z492"

# Paste request token here
request_token = "YpbJQEOZ0XWVY0CEZAzX3Bn0xBDZEjfu"

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
