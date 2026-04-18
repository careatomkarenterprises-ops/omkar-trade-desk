def generate_daily_report(self):
    """Report historical performance of patterns (not specific trades)"""
    # Instead of "X hits out of Y trades", use:
    # "Yesterday, 5 patterns formed. Of those, 3 showed movement towards statistical zone within 5 days."
    stats = self.get_pattern_performance()  # from JSON log
    msg = (f"📊 *Pattern Performance Update*\n"
           f"📈 Patterns detected yesterday: {stats['total']}\n"
           f"✅ Patterns that moved towards statistical zone: {stats['moved_towards_zone']}\n"
           f"📚 Historical win rate (last 30 days): {stats['win_rate']:.0f}%\n"
           f"🔗 *Upgrade to premium* for real-time pattern detection + methodology course.\n"
           f"{self.razorpay_link}")
    send_alert(msg, channel="@OmkarFree")
