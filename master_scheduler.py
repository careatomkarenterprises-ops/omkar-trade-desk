```python
import os
import subprocess
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
now = datetime.now(IST)

hour = now.hour
minute = now.minute

print("===================================")
print("🚀 MASTER AI TRADING SYSTEM")
print("===================================")
print(f"⏰ Current IST Time: {now}")
print("===================================")

# ---------------------------------------------------
# PRE-MARKET PREDICTOR
# 8:40 AM - 8:50 AM
# ---------------------------------------------------

if hour == 8 and 40 <= minute <= 50:
    print("📈 RUNNING PRE-MARKET PREDICTOR")

    subprocess.run(
        ["python", "-u", "run_market_prediction.py"],
        check=False
    )

# ---------------------------------------------------
# PRE-OPEN SCANNER
# 9:05 AM - 9:10 AM
# ---------------------------------------------------

if hour == 9 and 5 <= minute <= 10:
    print("🔥 RUNNING PRE-OPEN SCANNER")

    subprocess.run(
        ["python", "-u", "run_preopen_scanner.py"],
        check=False
    )

# ---------------------------------------------------
# OPENING CONFIRMATION
# 9:15 AM - 9:20 AM
# ---------------------------------------------------

if hour == 9 and 15 <= minute <= 20:
    print("🏦 RUNNING OPENING CONFIRMATION")

    subprocess.run(
        ["python", "-u", "run_opening_confirmation.py"],
        check=False
    )

# ---------------------------------------------------
# MARKET HOURS NEWS ENGINE
# Every 30 mins
# 9:30 AM - 3:30 PM
# ---------------------------------------------------

if 9 <= hour <= 15 and minute in [0, 30]:

    print("📰 RUNNING NEWS ENGINE")

    subprocess.run(
        ["python", "-u", "-m", "src.news.aggregator"],
        check=False
    )

# ---------------------------------------------------
# DELAYED FREE POSTS
# Every 30 mins
# ---------------------------------------------------

if 10 <= hour <= 15 and minute in [0, 30]:

    print("📢 RUNNING DELAYED FREE POSTS")

    subprocess.run(
        ["python", "-u", "src/scanner/delayed_poster.py"],
        check=False
    )

# ---------------------------------------------------
# MARKETING POSTS
# 11:00 AM / 2:00 PM / 5:00 PM
# ---------------------------------------------------

if (hour == 11 and minute <= 5) or \
   (hour == 14 and minute <= 5) or \
   (hour == 17 and minute <= 5):

    print("📣 RUNNING MARKETING ENGINE")

    subprocess.run(
        ["python", "-u", "src/marketing/promotion_engine.py"],
        check=False
    )

# ---------------------------------------------------
# MULTIBAGGER SCANNER
# 3:40 PM onwards
# ---------------------------------------------------

if hour == 15 and minute >= 40:

    print("🚀 RUNNING MULTIBAGGER SCANNER")

    subprocess.run(
        ["python", "-u", "run_multibagger_scanner.py"],
        check=False
    )

print("===================================")
print("✅ MASTER AI SYSTEM FINISHED")
print("===================================")
```
