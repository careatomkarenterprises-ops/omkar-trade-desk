import json

class EODEngine:

    def run(self, global_data):

        report = {
            "market_summary": self.summary(),
            "top_gainers": self.top_gainers(),
            "volume_breakouts": self.volume_stocks(),
            "sector_strength": self.sectors(),
            "global_context": global_data
        }

        self.save(report)
        self.print_report(report)

    def summary(self):
        return "Market showed mixed trend with selective buying in largecaps"

    def top_gainers(self):
        return ["ICICIPRULI", "SYMPHONY", "DIXON"]

    def volume_stocks(self):
        return ["RELIANCE", "INFY"]

    def sectors(self):
        return {
            "IT": "strong",
            "BANKING": "neutral",
            "AUTO": "positive"
        }

    def save(self, report):
        with open("data/eod.json", "w") as f:
            json.dump(report, f, indent=2)

    def print_report(self, report):
        print("\n📉 EOD REPORT")
        print("Top Gainers:", report["top_gainers"])
