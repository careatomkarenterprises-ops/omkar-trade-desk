import json
import os

class PerformanceTracker:

    def __init__(self):
        self.file = "data/performance.json"

        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)

    def log_trade(self, symbol, signal, result):
        with open(self.file, "r") as f:
            data = json.load(f)

        data.append({
            "symbol": symbol,
            "signal": signal,
            "result": result
        })

        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def get_accuracy(self):
        with open(self.file, "r") as f:
            data = json.load(f)

        if not data:
            return 0

        wins = len([d for d in data if d["result"] == "WIN"])
        return (wins / len(data)) * 100
