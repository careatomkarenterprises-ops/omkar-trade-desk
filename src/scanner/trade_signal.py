import pandas as pd

class TradeSignalGenerator:

    def __init__(self, fetcher):
        self.fetcher = fetcher

    def generate_signal(self):
        from src.scanner.volume_analyzer import VolumeSetupAnalyzer

        # Fetch 30-min data (NIFTY)
        df = self.fetcher.fetch_30min_data("NIFTY")

        if df is None or df.empty:
            return {"signal": "NONE", "reason": "No data"}

        analyzer = VolumeSetupAnalyzer()
        setups = analyzer.detect_setups(df)

        if not setups:
            return {"signal": "NONE", "reason": "No setup"}

        latest = setups[-1]

        top = latest['top']
        bottom = latest['bottom']
        range_size = latest['range']
        target_buy = latest['fab_50']
        target_sell = bottom - range_size * 0.5

        current_price = self.fetcher.get_current_futures_price()

        # ================= BUY =================
        if current_price > top:

            confidence = min(90, 50 + latest['candles'] * 5)

            return {
                "signal": "BUY",
                "entry": round(top, 2),
                "stop_loss": round(bottom, 2),
                "target": round(target_buy, 2),
                "confidence": f"{confidence}%"
            }

        # ================= SELL =================
        elif current_price < bottom:

            confidence = min(90, 50 + latest['candles'] * 5)

            return {
                "signal": "SELL",
                "entry": round(bottom, 2),
                "stop_loss": round(top, 2),
                "target": round(target_sell, 2),
                "confidence": f"{confidence}%"
            }

        else:
            return {
                "signal": "WAIT",
                "reason": "Price inside range"
            }
