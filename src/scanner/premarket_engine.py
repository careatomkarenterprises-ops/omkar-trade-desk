import logging
import json
import os

logger = logging.getLogger(__name__)

class PreMarketPredictionEngine:
    def __init__(self, data_fetcher, pattern_detector):
        self.fetcher = data_fetcher
        self.detector = pattern_detector
        self.min_strength = 0.40  # Lowered slightly to catch early moves

    def run(self, symbols=None, global_data=None):
        logger.info("🚀 Running Premarket Prediction Engine...")

        if not symbols:
            logger.warning("⚠ No symbols provided, using default watchlist")
            symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "LT", "AXISBANK", "KOTAKBANK", "ITC"]

        global_data = global_data or {}
        results = []

        for symbol in symbols:
            try:
                logger.info(f"🔍 Scanning {symbol}")
                df = self.fetcher.get_stock_data(symbol)

                if df is None or df.empty:
                    continue

                analysis = self.detector.analyze(symbol, df)

                if not analysis or not analysis.get("has_pattern"):
                    continue

                score = self.calculate_score(analysis, global_data)

                if score >= self.min_strength:
                    results.append({
                        "symbol": symbol,
                        "score": round(score, 2),
                        "price": df["close"].iloc[-1],
                        "signal": analysis.get("signal"),
                        "trend": analysis.get("trend")
                    })

            except Exception as e:
                logger.error(f"❌ Error scanning {symbol}: {e}")

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        top_results = results[:10]

        self.save(top_results)
        self.print_results(top_results)
        return top_results

    def calculate_score(self, analysis, global_data):
        score = 0.3 # Base score for having a pattern
        bias = global_data.get("overall_bias", "").upper()

        if "BULLISH" in bias and analysis.get("signal") == "BUY_SIGNAL":
            score += 0.4
        elif "BEARISH" in bias and analysis.get("signal") == "SELL_SIGNAL":
            score += 0.4
        
        return min(score, 1.0)

    def save(self, data):
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/premarket_predictions.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Save failed: {e}")

    def print_results(self, data):
        print("\n🔥 TOP PREMARKET SETUPS")
        print("========================")
        if not data:
            print("⚠ No strong setups found")
            return
        for d in data:
            print(f"{d['symbol']} | Score: {d['score']} | Signal: {d['signal']}")
