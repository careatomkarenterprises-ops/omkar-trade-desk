import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

import json
from src.telegram.poster import send_message


def post_delayed_alerts():

    print("===== DELAYED POSTER STARTED =====")

    cache_file = "data/last_scanner_cache.json"

    print("Checking cache file:", cache_file)

    if not os.path.exists(cache_file):
        print("❌ Cache file not found")
        return

    print("✅ Cache file found")

    with open(cache_file, 'r') as f:
        data = json.load(f)

    alerts = data.get("alerts", [])

    print("TOTAL ALERTS:", len(alerts))

    if not alerts:
        print("❌ No alerts available")
        return

    for alert in alerts:

        try:
            symbol = alert['symbol']
            setup = alert['setup']

            msg = (
                f"📊 Delayed Pattern (30 min ago) – {symbol}\n"
                f"📈 Setup: {setup['candles']} high-volume candles\n"
                f"🔴 Upper bound: {setup['top']}\n"
                f"🟢 Lower bound: {setup['bottom']}\n"
                f"🎯 Statistical zone: {setup['fab_50']}\n\n"
                f"⚠️ Educational purpose only"
            )

            print(f"Sending alert for {symbol}")

            send_message("free_main", msg)

            print(f"✅ Sent for {symbol}")

        except Exception as e:
            print("❌ ALERT ERROR:", str(e))

    try:
        os.remove(cache_file)
        print("✅ Cache file deleted")
    except Exception as e:
        print("❌ Cache delete failed:", str(e))

    print("===== DELAYED POSTER FINISHED =====")


if __name__ == "__main__":
    post_delayed_alerts()
