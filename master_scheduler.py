from datetime import datetime
import os

ist_now = datetime.now()

hour = ist_now.hour
minute = ist_now.minute

current = f"{hour:02d}:{minute:02d}"

print("===================================")
print("MASTER AI SCHEDULER")
print("Current IST:", current)
print("===================================")

# -----------------------------------
# PRE MARKET
# -----------------------------------

if current == "08:40":
    print("RUNNING PRE-MARKET PREDICTOR")
    os.system("python run_market_prediction.py")

# -----------------------------------
# PRE OPEN
# -----------------------------------

if current == "09:05":
    print("RUNNING PRE-OPEN SCANNER")
    os.system("python run_preopen_scanner.py")

# -----------------------------------
# OPENING CONFIRMATION
# -----------------------------------

if current == "09:15":
    print("RUNNING OPENING CONFIRMATION")
    os.system("python run_opening_confirmation.py")

# -----------------------------------
# NEWS ENGINE EVERY 30 MINS
# -----------------------------------

if minute in [0, 30]:
    print("RUNNING NEWS ENGINE")
    os.system("python -m src.news.aggregator")

# -----------------------------------
# DELAYED FREE POSTS
# -----------------------------------

if minute in [0, 30]:
    print("RUNNING DELAYED POSTS")
    os.system("python src/scanner/delayed_poster.py")

# -----------------------------------
# MARKETING
# -----------------------------------

if current in ["11:30", "14:30", "17:30"]:
    print("RUNNING MARKETING ENGINE")
    os.system("python src/marketing/promotion_engine.py")

# -----------------------------------
# MULTIBAGGER
# -----------------------------------

if current == "16:00":
    print("RUNNING MULTIBAGGER SCANNER")
    os.system("python run_multibagger_scanner.py")

print("===================================")
print("MASTER SCHEDULER COMPLETED")
print("===================================")
