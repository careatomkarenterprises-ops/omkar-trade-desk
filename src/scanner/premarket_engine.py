import json
from datetime import datetime

class PreMarketEngine:

    def run(self, global_data):

        report = {
            "time": str(datetime.now()),
            "market_bias": self.get_bias(global_data),
            "top_focus": self.watchlist(),
            "strategy": "Breakout + Volume Confirmation",
            "global_summary": global_data
        }

        self.save(report)
        self.print_report(report)

    def get_bias(self, data):

        if data["gift_nifty"]["trend"] == "bullish":
            return "POSITIVE START EXPECTED"
        return "MIXED / SIDEWAYS"

    def watchlist(self):
        return [
            "NIFTY",
            "BANKNIFTY",
            "RELIANCE",
            "INFY",
            "TATAMOTORS"
        ]

    def save(self, report):
        with open("data/premarket.json", "w") as f:
            json.dump(report, f, indent=2)

    def print_report(self, report):
        print("\n🔥 PREMARKET REPORT")
        print("===================")
        print("Bias:", report["market_bias"])
        print("Watchlist:", report["top_focus"])
