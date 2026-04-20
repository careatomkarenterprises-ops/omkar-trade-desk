import json
import os
from datetime import datetime, timedelta
from src.telegram.poster import send_message

class PromotionEngine:
    def __init__(self, log_file="data/performance.json"):
        self.log_file = log_file
        self.razorpay_link = os.getenv("RAZORPAY_LINK", "")
        self._ensure_log_file()

    def _ensure_log_file(self):
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump({"daily": {}, "all_time": {"total_patterns": 0, "total_moved": 0, "best_move": 0}}, f)

    def log_pattern_performance(self, pattern_symbol, moved_towards_zone, price_move_percent):
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            data = {"daily": {}, "all_time": {"total_patterns": 0, "total_moved": 0, "best_move": 0}}

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in data["daily"]:
            data["daily"][today] = {"total": 0, "moved_towards": 0, "moves": []}
        data["daily"][today]["total"] += 1
        if moved_towards_zone:
            data["daily"][today]["moved_towards"] += 1
            data["daily"][today]["moves"].append(price_move_percent)
            data["all_time"]["total_moved"] += 1
            if price_move_percent > data["all_time"]["best_move"]:
                data["all_time"]["best_move"] = price_move_percent
        data["all_time"]["total_patterns"] += 1

        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_daily_report(self):
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        stats = data["daily"].get(today, {"total": 0, "moved_towards": 0, "moves": []})

        if stats["total"] == 0:
            msg = "📊 *Pattern Performance*: No qualifying patterns today."
        else:
            ratio = (stats["moved_towards"] / stats["total"]) * 100
            best_move = max(stats["moves"]) if stats["moves"] else 0
            msg = (f"📈 *Daily Performance Report*\n"
                   f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
                   f"✅ Patterns moved towards statistical zone: {stats['moved_towards']} / {stats['total']} ({ratio:.0f}%)\n"
                   f"🏆 Best observed move: +{best_move:.2f}%\n\n"
                   f"🚀 *Real-time alerts:* {self.razorpay_link}\n⚠️ Educational purpose only.")

        send_message("free_main", msg)
        return stats

if __name__ == "__main__":
    engine = PromotionEngine()
    engine.generate_daily_report()
