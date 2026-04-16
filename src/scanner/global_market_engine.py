class GlobalMarketEngine:

    def run(self):

        data = {
            "us_market": self.us_market(),
            "asia_market": self.asia_market(),
            "gift_nifty": self.gift_nifty(),
            "crypto": self.crypto_sentiment(),
            "crude_oil": self.crude_oil()
        }

        return data

    def us_market(self):
        return {
            "nasdaq": "neutral",
            "dow": "positive",
            "snp500": "slightly positive"
        }

    def asia_market(self):
        return {
            "nikkei": "positive",
            "hang_seng": "mixed",
            "sgx": "gap up expected"
        }

    def gift_nifty(self):
        return {
            "trend": "bullish",
            "gap": "+80 points expected"
        }

    def crypto_sentiment(self):
        return {
            "btc": "stable",
            "eth": "positive bias"
        }

    def crude_oil(self):
        return {
            "trend": "slightly bullish"
        }
