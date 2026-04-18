import json
import os
from datetime import datetime
from src.telegram.poster import send_alert

class PromotionEngine:
    def __init__(self, log_file="data/performance.json"):
        self.log_file = log_file
        self.razorpay_link = os.getenv("RAZORPAY_LINK", "")

    def log_pattern_performance(self, pattern_symbol, moved_towards_zone, price_move_percent):
        """Log how patterns behaved (for trust building)"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            data = {"daily": {}}

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in data["daily"]:
            data["daily"][today] = {"total": 0, "moved_towards": 0, "moves": []}

        data["daily"][today]["total"] += 1
        if moved_towards_zone:
            data["daily"][today]["moved_towards"] += 1
            data["daily"][today]["moves"].append(price_move_percent)

        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_daily_report(self):
        """Send performance report to free channels (trust building)"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            data = {"daily": {}}

        today = datetime.now().strftime("%Y-%m-%d")
        stats = data["daily"].get(today, {"total": 0, "moved_towards": 0, "moves": []})

        if stats["total"] == 0:
            msg = "📊 *Pattern Performance*: No qualifying patterns yesterday. Stay tuned for today's observations."
        else:
            ratio = (stats["moved_towards"] / stats["total"]) * 100
            best_move = max(stats["moves"]) if stats["moves"] else 0
            msg = (f"📈 *Pattern Performance Report*\n"
                   f"✅ Patterns that moved towards statistical zone: {stats['moved_towards']} / {stats['total']} ({ratio:.0f}%)\n"
                   f"🏆 Best observed move: {best_move:.2f}%\n"
                   f"📚 *Learn the methodology*: {self.razorpay_link}")

        send_alert(msg, channel="@OmkarFree")
        return stats
