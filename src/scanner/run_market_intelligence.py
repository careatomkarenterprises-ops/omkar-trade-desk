import datetime

from src.scanner.premarket_engine import PreMarketEngine
from src.scanner.eod_engine import EODEngine
from src.scanner.learning_engine import LearningEngine
from src.scanner.global_market_engine import GlobalMarketEngine


def main():

    now = datetime.datetime.now()

    global_engine = GlobalMarketEngine()

    # Always generate global context first
    global_data = global_engine.run()

    # PREMARKET (before 9:15 AM)
    if now.hour < 9:

        print("🚀 Running PREMARKET ENGINE")
        engine = PreMarketEngine()
        engine.run(global_data)

    # MARKET HOURS (skip heavy processing)
    elif 9 <= now.hour < 16:
        print("📊 Market Live - Scanner mode should run separately")

    # EOD ENGINE (after 3:30 PM)
    else:

        print("📉 Running EOD ENGINE")
        eod = EODEngine()
        eod.run(global_data)

        print("🧠 Running LEARNING ENGINE")
        learn = LearningEngine()
        learn.run(global_data)


if __name__ == "__main__":
    main()
