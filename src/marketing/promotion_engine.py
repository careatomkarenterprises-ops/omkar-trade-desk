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
        """Create log file with initial structure if not exists"""
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            initial_data = {
                "daily": {},
                "weekly": {},
                "monthly": {},
                "all_time": {"total_patterns": 0, "total_moved": 0, "best_move": 0, "best_symbol": ""}
            }
            with open(self.log_file, 'w') as f:
                json.dump(initial_data, f, indent=2)

    def log_pattern_performance(self, pattern_symbol, moved_towards_zone, price_move_percent):
        """Log each pattern's performance for tracking"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            data = {"daily": {}, "weekly": {}, "monthly": {}, "all_time": {"total_patterns": 0, "total_moved": 0, "best_move": 0, "best_symbol": ""}}

        today = datetime.now().strftime("%Y-%m-%d")
        week_key = datetime.now().strftime("%Y-W%W")
        month_key = datetime.now().strftime("%Y-%m")

        # Update daily
        if today not in data["daily"]:
            data["daily"][today] = {"total": 0, "moved_towards": 0, "moves": []}
        data["daily"][today]["total"] += 1
        if moved_towards_zone:
            data["daily"][today]["moved_towards"] += 1
            data["daily"][today]["moves"].append(price_move_percent)

        # Update weekly
        if week_key not in data["weekly"]:
            data["weekly"][week_key] = {"total": 0, "moved_towards": 0, "moves": []}
        data["weekly"][week_key]["total"] += 1
        if moved_towards_zone:
            data["weekly"][week_key]["moved_towards"] += 1
            data["weekly"][week_key]["moves"].append(price_move_percent)

        # Update monthly
        if month_key not in data["monthly"]:
            data["monthly"][month_key] = {"total": 0, "moved_towards": 0, "moves": []}
        data["monthly"][month_key]["total"] += 1
        if moved_towards_zone:
            data["monthly"][month_key]["moved_towards"] += 1
            data["monthly"][month_key]["moves"].append(price_move_percent)

        # Update all-time
        data["all_time"]["total_patterns"] += 1
        if moved_towards_zone:
            data["all_time"]["total_moved"] += 1
            if price_move_percent > data["all_time"]["best_move"]:
                data["all_time"]["best_move"] = price_move_percent
                data["all_time"]["best_symbol"] = pattern_symbol

        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_daily_report(self):
        """Send daily performance report to free channel"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            self._ensure_log_file()
            data = json.load(open(self.log_file))

        today = datetime.now().strftime("%Y-%m-%d")
        stats = data["daily"].get(today, {"total": 0, "moved_towards": 0, "moves": []})

        # Get yesterday's stats for comparison
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_stats = data["daily"].get(yesterday, {"total": 0, "moved_towards": 0, "moves": []})

        if stats["total"] == 0:
            msg = "📊 *Pattern Performance*: No qualifying patterns detected today."
        else:
            ratio = (stats["moved_towards"] / stats["total"]) * 100
            best_move = max(stats["moves"]) if stats["moves"] else 0
            
            msg = (f"📈 *Daily Performance Report*\n"
                   f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
                   f"✅ Patterns that moved towards statistical zone: {stats['moved_towards']} / {stats['total']} ({ratio:.0f}%)\n"
                   f"🏆 Best observed move: +{best_move:.2f}%\n")
            
            if yesterday_stats["total"] > 0:
                yesterday_ratio = (yesterday_stats["moved_towards"] / yesterday_stats["total"]) * 100
                msg += f"📊 Yesterday's win rate: {yesterday_ratio:.0f}%\n"
            
            msg += f"\n🚀 *Real-time alerts*: {self.razorpay_link}\n⚠️ Educational purpose only."
        
        send_message("free_main", msg)
        return stats

    def generate_weekly_report(self):
        """Send weekly performance report every Friday"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            return

        week_key = datetime.now().strftime("%Y-W%W")
        stats = data["weekly"].get(week_key, {"total": 0, "moved_towards": 0, "moves": []})

        if stats["total"] == 0:
            return

        ratio = (stats["moved_towards"] / stats["total"]) * 100
        best_move = max(stats["moves"]) if stats["moves"] else 0
        avg_move = sum(stats["moves"]) / len(stats["moves"]) if stats["moves"] else 0

        msg = (f"📊 *Weekly Performance Report*\n"
               f"📅 Week of {datetime.now().strftime('%B %d, %Y')}\n\n"
               f"✅ Total patterns: {stats['total']}\n"
               f"📈 Win rate: {ratio:.0f}%\n"
               f"🏆 Best move: +{best_move:.2f}%\n"
               f"📊 Average move: +{avg_move:.2f}%\n\n"
               f"💎 *Premium subscribers get real-time alerts.*\n"
               f"🔗 Subscribe: {self.razorpay_link}\n⚠️ Educational only.")

        send_message("free_main", msg)
        send_message("free_signals", msg)

    def generate_monthly_report(self):
        """Send monthly performance report on the 1st of each month"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            return

        month_key = datetime.now().strftime("%Y-%m")
        stats = data["monthly"].get(month_key, {"total": 0, "moved_towards": 0, "moves": []})

        if stats["total"] == 0:
            return

        ratio = (stats["moved_towards"] / stats["total"]) * 100
        best_move = max(stats["moves"]) if stats["moves"] else 0
        all_time = data.get("all_time", {})

        msg = (f"📊 *Monthly Performance Report*\n"
               f"📅 {datetime.now().strftime('%B %Y')}\n\n"
               f"✅ Total patterns: {stats['total']}\n"
               f"📈 Monthly win rate: {ratio:.0f}%\n"
               f"🏆 Best move this month: +{best_move:.2f}%\n\n"
               f"🏅 *All-Time Best Move:* +{all_time.get('best_move', 0):.2f}% on {all_time.get('best_symbol', 'N/A')}\n"
               f"📊 All-time win rate: {(all_time.get('total_moved', 0) / max(1, all_time.get('total_patterns', 1))) * 100:.0f}%\n\n"
               f"🚀 *Join premium for real-time access:* {self.razorpay_link}\n⚠️ Educational only.")

        send_message("free_main", msg)
        send_message("free_signals", msg)

    def generate_urgency_message(self):
        """Create urgency for subscription (run every Monday morning)"""
        msg = (f"🔥 *Limited Time Offer*\n\n"
               f"Premium subscription price increases next month.\n"
               f"Lock in current rate: ₹999/month\n\n"
               f"✅ Real-time intraday patterns\n"
               f"✅ Currency & commodity alerts\n"
               f"✅ F&O and index futures\n\n"
               f"🔗 Subscribe now: {self.razorpay_link}\n"
               f"⚠️ Prices subject to change without notice.")

        send_message("free_main", msg)
        send_message("free_signals", msg)

    def generate_testimonial_message(self):
        """Generate trust-building message with best performance"""
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
        except:
            return

        all_time = data.get("all_time", {})
        if all_time.get("best_move", 0) > 0:
            msg = (f"🏆 *Real Result*\n\n"
                   f"Our volume setup detected a move of +{all_time['best_move']:.2f}% on {all_time.get('best_symbol', 'a stock')}.\n\n"
                   f"Premium subscribers received this alert in real-time.\n\n"
                   f"🔗 Get real-time alerts: {self.razorpay_link}\n⚠️ Past performance does not guarantee future results.")

            send_message("free_main", msg)

    def generate_comparison_message(self):
        """Show side-by-side comparison of free vs premium"""
        msg = (f"📊 *Free vs Premium – What's the Difference?*\n\n"
               f"🔵 *Free Channel (@OmkarTradeDesk)*\n"
               f"   • Pre-market outlook\n"
               f"   • Delayed patterns (30 min late)\n"
               f"   • Daily performance reports\n\n"
               f"🟡 *Premium Channel (@Omkar_Pro)*\n"
               f"   • Real-time patterns (instant)\n"
               f"   • Currency & commodity alerts\n"
               f"   • F&O and index futures\n"
               f"   • Priority support\n\n"
               f"🚀 Upgrade: {self.razorpay_link}")

        send_message("free_main", msg)
        send_message("free_signals", msg)

# Run all reports based on day of week
if __name__ == "__main__":
    engine = PromotionEngine()
    engine.generate_daily_report()
    
    # Weekly report on Fridays (weekday = 4)
    if datetime.now().weekday() == 4:
        engine.generate_weekly_report()
    
    # Monthly report on 1st day of month
    if datetime.now().day == 1:
        engine.generate_monthly_report()
    
    # Urgency message on Mondays (weekday = 0)
    if datetime.now().weekday() == 0:
        engine.generate_urgency_message()
    
    # Testimonial every Wednesday (weekday = 2)
    if datetime.now().weekday() == 2:
        engine.generate_testimonial_message()
    
    # Comparison message every Sunday (weekday = 6)
    if datetime.now().weekday() == 6:
        engine.generate_comparison_message()