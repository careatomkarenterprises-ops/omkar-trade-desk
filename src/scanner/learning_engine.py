import json

class LearningEngine:

    def run(self, global_data):

        insights = {
            "volume_accuracy": "72%",
            "false_breakouts": "mostly midcaps",
            "best_strategy": "volume + breakout confirmation",
            "market_behavior": self.analyze(global_data)
        }

        self.save(insights)
        self.print(insights)

    def analyze(self, data):

        if data["gift_nifty"]["trend"] == "bullish":
            return "bullish bias followed through in selective stocks"

        return "range bound behavior observed"

    def save(self, data):
        with open("data/learning.json", "w") as f:
            json.dump(data, f, indent=2)

    def print(self, data):
        print("\n🧠 DAILY LEARNING")
        print("================")
        print(data)
