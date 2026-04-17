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
        
        # ✅ FIX: Construct the message string to return to the Controller
        message = "📊 *OMKAR EOD MARKET REVIEW*\n\n"
        message += f"📝 *Summary:* {report['market_summary']}\n\n"
        message += f"📈 *Top Gainers:* {', '.join(report['top_gainers'])}\n"
        message += f"🔥 *Volume Breakouts:* {', '.join(report['volume_breakouts'])}\n\n"
        message += "⚡ *Sector Pulse:*\n"
        for sector, strength in report['sector_strength'].items():
            message += f"• {sector}: {strength.upper()}\n"
            
        return message

    def summary(self):
        return "Market showed mixed trend with selective buying in largecaps"

    def top_gainers(self):
        return ["ICICIPRULI", "SYMPHONY", "DIXON"]

    def volume_stocks(self):
        return ["RELIANCE", "INFY"]

    def sectors(self):
        return {"IT": "strong", "BANKING": "neutral", "AUTO": "positive"}

    def save(self, report):
        with open("data/eod.json", "w") as f:
            json.dump(report, f, indent=2)
