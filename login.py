from kiteconnect import KiteConnect

api_key = "y9td8bzzuoobxp2b"
api_secret = "wqk99q83t3zcufo0m354bzpegl57z492"

kite = KiteConnect(api_key=api_key)

print("Login URL:", kite.login_url())

# 👉 Open URL, login manually, then paste request_token here
request_token = input("Enter request token: ")

data = kite.generate_session(request_token, api_secret=api_secret)
access_token = data["access_token"]

print("ACCESS TOKEN:", access_token)
