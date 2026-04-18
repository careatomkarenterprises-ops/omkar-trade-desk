import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
from src.telegram.poster import send_message

def post_delayed_alerts():
    cache_file = "data/last_scanner_cache.json"
    if not os.path.exists(cache_file):
        return
    with open(cache_file, 'r') as f:
        data = json.load(f)
    alerts = data.get("alerts", [])
    for alert in alerts:
        symbol = alert['symbol']
        setup = alert['setup']
        msg = (f"📊 *Delayed Pattern* (30 min ago) – {symbol}\n"
               f"📈 Setup: {setup['candles']} high-volume candles\n"
               f"🔴 Upper bound: {setup['top']}\n"
               f"🟢 Lower bound: {setup['bottom']}\n"
               f"🎯 Statistical zone: {setup['fab_50']}\n⚠️ Educational.")
        send_message("free_main", msg)
    os.remove(cache_file)

if __name__ == "__main__":
    post_delayed_alerts()
