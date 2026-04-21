from src.scanner.premarket_engine_v2 import PreMarketEngineV2
from src.telegram.telegram_report_engine import TelegramReportEngine


class MarketPredictorV2:

    def __init__(self):
        self.engine = PreMarketEngineV2()
        self.telegram = TelegramReportEngine()

    def run(self):

        data = self.engine.run()

        msg = f"""
📊 INSTITUTIONAL PRE-MARKET DASHBOARD

🌍 GLOBAL: {data['global_sentiment']}

📊 NIFTY PROBABILITY:
UP: {data['nifty'][0]}% | DOWN: {data['nifty'][1]}%

📊 BANKNIFTY PROBABILITY:
UP: {data['banknifty'][0]}% | DOWN: {data['banknifty'][1]}%

⚡ VOLATILITY: {data['volatility']}

📉 OPTIONS FLOW: {data['options']} (PCR {data['pcr']})

🔥 SMART MONEY SCORE: {data['smart_money']}/100

⏰ {data['timestamp']}
⚠️ Educational use only
"""

        self.telegram.send_message(msg)


if __name__ == "__main__":
    MarketPredictorV2().run()
