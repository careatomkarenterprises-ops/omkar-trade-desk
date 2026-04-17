import logging
import json

logger = logging.getLogger(__name__)


class PreMarketPredictionEngine:

    def __init__(self, data_fetcher, pattern_detector):
        self.fetcher = data_fetcher
        self.detector = pattern_detector
        self.min_strength = 0.60

    # -----------------------------
    # MAIN ENTRY
    # -----------------------------
    def run(self, symbols=None, global_data=None):

        logger.info("🚀 Running Premarket Prediction Engine...")

        # ✅ DEFAULT SYMBOLS
        if not symbols:
            logger.warning("⚠ No symbols provided, using default watchlist")
            symbols = [
                "RELIANCE", "TCS", "INFY", "HDFCBANK",
                "ICICIBANK", "SBIN", "LT", "AXISBANK",
                "KOTAKBANK", "ITC"
            ]

        if not global_data:
            global_data = {}

        results = []

        for symbol in symbols:

            try:
                logger.info(f"🔍 Scanning {symbol}")

                df = self.fetcher.get_stock_data(symbol)

                if df is None or df.empty:
                    logger.warning(f"⚠ No data for {symbol}")
                    continue

                analysis = self.detector.analyze(symbol, df)

                if not analysis or not analysis.get("has_pattern"):
                    continue

                score = self.calculate_score(analysis, global_data)

                if score >= self.min_strength:
                    results.append({
                        "symbol": symbol,
                        "score": round(score, 2),
                        "price": analysis.get("price"),
                        "trigger": analysis.get("trigger"),
                        "surge": analysis.get("surge_ratio"),
                        "support": analysis.get("support"),
                        "resistance": analysis.get("resistance")
                    })

            except Exception as e:
                logger.error(f"❌ Error scanning {symbol}: {e}")

        # SORT
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        top_results = results[:10]

        self.save(top_results)
        self.print_results(top_results)

        logger.info("✅ Premarket Completed")

        return top_results

    # -----------------------------
    def calculate_score(self, analysis, global_data):

        score = 0

        surge = analysis.get("surge_ratio", 1)
        score += min(surge / 3, 0.4)

        strength = analysis.get("strength", 0)
        score += strength * 0.3

        bias = global_data.get("overall_bias", "")

        if bias == "BULLISH SETUP":
            score += 0.3
        elif bias == "BEARISH SETUP":
            score -= 0.2

        if "BREAKOUT" in str(analysis.get("trigger", "")):
            score += 0.2

        return min(max(score, 0), 1)

    # -----------------------------
    def save(self, data):
        try:
            with open("data/premarket_predictions.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Save failed: {e}")

    # -----------------------------
    def print_results(self, data):

        print("\n🔥 TOP PREMARKET SETUPS")
        print("========================")

        if not data:
            print("⚠ No strong setups found")
            return

        for d in data:
            print(
                f"{d['symbol']} | Score: {d['score']} | "
                f"Price: {d['price']} | Surge: {d['surge']}x"
            )
