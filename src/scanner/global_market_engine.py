"""
Global Market Engine - REAL DATA VERSION (Free Sources)
- India + Global markets sentiment
- Gift Nifty proxy
- US market proxy (Yahoo Finance)
- Currency + crude oil trend
- News sentiment fallback (simple heuristic)
"""

import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GlobalMarketEngine:

    def run(self):

        data = {
            "timestamp": str(datetime.now()),
            "us_market": self.us_market(),
            "asia_market": self.asia_market(),
            "gift_nifty": self.gift_nifty(),
            "currency": self.currency(),
            "crude_oil": self.crude_oil(),
            "overall_bias": ""
        }

        data["overall_bias"] = self.compute_bias(data)

        logger.info(f"🌍 Global Market Bias: {data['overall_bias']}")

        return data

    # -------------------------------
    # 🌎 US MARKET (Yahoo Finance proxy)
    # -------------------------------
    def us_market(self):

        try:
            url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=^DJI,^IXIC,^GSPC"
            r = requests.get(url, timeout=5)
            data = r.json()["quoteResponse"]["result"]

            result = {}

            for item in data:
                name = item.get("shortName", "")
                change = item.get("regularMarketChangePercent", 0)

                if "^DJI" in item["symbol"]:
                    result["dow"] = round(change, 2)
                elif "^IXIC" in item["symbol"]:
                    result["nasdaq"] = round(change, 2)
                elif "^GSPC" in item["symbol"]:
                    result["sp500"] = round(change, 2)

            return result

        except Exception as e:
            logger.warning(f"US market fetch failed: {e}")
            return {"dow": 0, "nasdaq": 0, "sp500": 0}

    # -------------------------------
    # 🌏 ASIA MARKETS (simple proxy)
    # -------------------------------
    def asia_market(self):

        try:
            url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=^NSEI,^N225,^HSI"
            r = requests.get(url, timeout=5)
            data = r.json()["quoteResponse"]["result"]

            result = {}

            for item in data:
                change = item.get("regularMarketChangePercent", 0)

                if "^NSEI" in item["symbol"]:
                    result["nifty"] = round(change, 2)
                elif "^N225" in item["symbol"]:
                    result["nikkei"] = round(change, 2)
                elif "^HSI" in item["symbol"]:
                    result["hang_seng"] = round(change, 2)

            return result

        except Exception as e:
            logger.warning(f"Asia market fetch failed: {e}")
            return {"nifty": 0, "nikkei": 0, "hang_seng": 0}

    # -------------------------------
    # 🇮🇳 GIFT NIFTY (proxy logic)
    # -------------------------------
    def gift_nifty(self):

        try:
            # fallback proxy using NIFTY futures sentiment
            url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=^NSEI"
            r = requests.get(url, timeout=5)
            data = r.json()["quoteResponse"]["result"][0]

            change = data.get("regularMarketChangePercent", 0)

            return {
                "trend": "bullish" if change > 0 else "bearish",
                "change": round(change, 2)
            }

        except Exception:
            return {
                "trend": "neutral",
                "change": 0
            }

    # -------------------------------
    # 💱 CURRENCY (USD/INR proxy)
    # -------------------------------
    def currency(self):

        try:
            url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=INR=X"
            r = requests.get(url, timeout=5)
            data = r.json()["quoteResponse"]["result"][0]

            change = data.get("regularMarketChangePercent", 0)

            return {
                "usd_inr": round(change, 2),
                "trend": "weak INR" if change > 0 else "strong INR"
            }

        except Exception:
            return {"usd_inr": 0, "trend": "neutral"}

    # -------------------------------
    # 🛢️ CRUDE OIL
    # -------------------------------
    def crude_oil(self):

        try:
            url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=CL=F"
            r = requests.get(url, timeout=5)
            data = r.json()["quoteResponse"]["result"][0]

            change = data.get("regularMarketChangePercent", 0)

            return {
                "trend": "bullish" if change > 0 else "bearish",
                "change": round(change, 2)
            }

        except Exception:
            return {"trend": "neutral", "change": 0}

    # -------------------------------
    # 🧠 FINAL BIAS ENGINE
    # -------------------------------
    def compute_bias(self, data):

        score = 0

        # US market weight
        score += data["us_market"].get("nasdaq", 0)

        # Asia
        score += data["asia_market"].get("nifty", 0)

        # Crude oil
        if data["crude_oil"]["trend"] == "bullish":
            score -= 0.5
        else:
            score += 0.5

        # Currency
        if data["currency"]["trend"] == "weak INR":
            score += 0.3

        # Final decision
        if score > 1:
            return "BULLISH SETUP"
        elif score < -1:
            return "BEARISH SETUP"
        else:
            return "SIDEWAYS / STOCK SPECIFIC"
