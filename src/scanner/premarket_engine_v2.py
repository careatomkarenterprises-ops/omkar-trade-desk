import yfinance as yf
import numpy as np
from datetime import datetime


class PreMarketEngineV2:

    # ============================
    # GLOBAL MARKET DATA
    # ============================
    def get_global_sentiment(self):

        try:
            us = yf.download("^GSPC", period="5d")["Close"].pct_change().mean()
            nasdaq = yf.download("^IXIC", period="5d")["Close"].pct_change().mean()

            asia = yf.download("^N225", period="5d")["Close"].pct_change().mean()

            score = (us + nasdaq + asia) * 100

            if score > 0.2:
                return "RISK-ON"
            elif score < -0.2:
                return "RISK-OFF"
            return "NEUTRAL"

        except:
            return "NEUTRAL"

    # ============================
    # NIFTY / BANKNIFTY PROBABILITY
    # ============================
    def probability_score(self, symbol):

        try:
            df = yf.download(symbol, period="10d")

            returns = df["Close"].pct_change().dropna()

            momentum = returns.mean()
            volatility = returns.std()

            score_up = max(0, 50 + (momentum * 1000) - (volatility * 100))
            score_down = 100 - score_up

            return round(score_up, 2), round(score_down, 2)

        except:
            return 50, 50

    # ============================
    # VOLATILITY ENGINE
    # ============================
    def volatility_state(self):

        try:
            vix = yf.download("^VIX", period="5d")["Close"].mean()

            if vix > 20:
                return "HIGH"
            elif vix > 15:
                return "NORMAL"
            return "LOW"

        except:
            return "NORMAL"

    # ============================
    # OPTIONS SENTIMENT (SIMULATED PCR)
    # ============================
    def options_sentiment(self, nifty_up):

        pcr = 1 - (nifty_up / 100)

        if pcr > 0.55:
            return "BEARISH BIAS", round(pcr, 2)
        elif pcr < 0.45:
            return "BULLISH BIAS", round(pcr, 2)
        return "NEUTRAL", round(pcr, 2)

    # ============================
    # SMART MONEY FUSION SCORE
    # ============================
    def smart_money_score(self, prob_up, volatility):

        base = prob_up

        if volatility == "HIGH":
            base += 5
        elif volatility == "LOW":
            base -= 5

        return min(100, max(0, round(base)))

    # ============================
    # MAIN ENGINE
    # ============================
    def run(self):

        global_sentiment = self.get_global_sentiment()

        nifty_up, nifty_down = self.probability_score("^NSEI")
        bank_up, bank_down = self.probability_score("^NSEBANK")

        volatility = self.volatility_state()

        options_bias, pcr = self.options_sentiment(nifty_up)

        smart_score = self.smart_money_score(nifty_up, volatility)

        return {
            "global_sentiment": global_sentiment,
            "nifty": (nifty_up, nifty_down),
            "banknifty": (bank_up, bank_down),
            "volatility": volatility,
            "options": options_bias,
            "pcr": pcr,
            "smart_money": smart_score,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
