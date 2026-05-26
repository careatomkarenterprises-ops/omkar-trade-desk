from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException

api_key = "y9td8bzzuoobxp2b"
api_secret = "wqk99q83t3zcufo0m354bzpegl57z492"

request_token = input("Enter request token: ")

kite = KiteConnect(api_key=api_key)

try:
    data = kite.generate_session(
        request_token=request_token,
        api_secret=api_secret
    )

    print("\n✅ SUCCESS")
    print("ACCESS TOKEN:", data["access_token"])

except KiteException as e:
    print("\n❌ Kite API Error:", e)

except Exception as e:
    print("\n❌ General Error:", e)
