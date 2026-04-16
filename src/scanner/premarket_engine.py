"""
Premarket Prediction Engine - Institutional Setup Scanner
"""

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
    def run(self, symbols, global_data):

        logger.info("🚀 Running Premarket Prediction Engine...")

        results = []

        for symbol in symbols:

            try:
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
                        "price": analysis["price"],
                        "trigger": analysis["trigger"],
                        "surge": analysis["surge_ratio"],
                        "support": analysis["support"],
                        "resistance": analysis["resistance"]
                    })

            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")

        # Sort best setups first
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        # Top 10 only
        top_results = results[:10]

        self.save(top_results)
        self.print(top_results)

        return top_results

    # -----------------------------
    # SCORING ENGINE (VERY IMPORTANT)
    # -----------------------------
    def calculate_score(self, analysis, global_data):

        score = 0

        # 1. Volume strength
        surge = analysis.get("surge_ratio", 1)
        score += min(surge / 3, 0.4)

        # 2. Pattern strength
        strength = analysis.get("strength", 0)
        score += strength * 0.3

        # 3. Global market bias influence
        bias = global_data.get("overall_bias", "")

        if bias == "BULLISH SETUP":
            score += 0.3
        elif bias == "BEARISH SETUP":
            score -= 0.2

        # 4. Breakout preference
        if "BREAKOUT" in analysis.get("trigger", ""):
            score += 0.2

        return min(max(score, 0), 1)

    # -----------------------------
    # SAVE OUTPUT
    # -----------------------------
    def save(self, data):

        with open("data/premarket_predictions.json", "w") as f:
            json.dump(data, f, indent=2)

    # -----------------------------
    # PRINT OUTPUT
    # -----------------------------
    def print(self, data):

        print("\n🔥 TOP PREMARKET SETUPS")
        print("========================")

        for d in data:
            print(
                f"{d['symbol']} | Score: {d['score']} | "
                f"Price: {d['price']} | Surge: {d['surge']}x"
            )
