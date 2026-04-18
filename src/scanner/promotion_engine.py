import json
import os
from datetime import datetime
from src.telegram.poster import send_alert

class PromotionEngine:
    def __init__(self, log_file="data/performance.json"):
        self.log_file = log_file
        self.razorpay_link = os.getenv("RAZORPAY_LINK", "")

    def log_performance(self, signal_symbol, hit_target, gain_percent):
        """Called when a signal hits target or expires"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            data = {"daily": {}}

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in data["daily"]:
            data["daily"][today] = {"hits": 0, "total": 0, "gains": []}

        data["daily"][today]["total"] += 1
        if hit_target:
            data["daily"][today]["hits"] += 1
            data["daily"][today]["gains"].append(gain_percent)

        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_daily_report(self):
        """Send performance report to free channels at 9:30 AM & 9:00 PM"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            data = {"daily": {}}

        today = datetime.now().strftime("%Y-%m-%d")
        stats = data["daily"].get(today, {"hits": 0, "total": 0, "gains": []})

        if stats["total"] == 0:
            msg = "📊 *No premium signals triggered yesterday.* Stay tuned for today's setups."
        else:
            win_rate = (stats["hits"] / stats["total"]) * 100
            best_gain = max(stats["gains"]) if stats["gains"] else 0
            msg = (f"📈 *Yesterday's Performance Report*\n"
                   f"✅ Signals hit target: {stats['hits']} / {stats['total']} ({win_rate:.0f}%)\n"
                   f"🏆 Best gain: +{best_gain:.2f}%\n"
                   f"🔗 *Get real-time alerts*: {self.razorpay_link}")

        send_alert(msg, channel="@OmkarFree")
        return stats
