import pandas as pd
import logging
from datetime import datetime, timedelta
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)

"""
Omkar Trade Services - Swing Agent
Logic: VSA (Volume Spread Analysis) - Shakeouts & Supply Tests
"""
class SwingAgent:
    def __init__(self, kite_instance):
        self.kite = kite_instance
        self.telegram = TelegramPoster()
        # Add your watch list here
        self.watchlist = ["NSE:RELIANCE", "NSE:HDFCBANK", "NSE:TCS", "NSE:INFY", "NSE:ICICIBANK"]

    def run(self):
        """Master entry point called by System Controller"""
        logger.info("📡 SwingAgent: Starting VSA Shakeout Scan...")
        results = []
        
        for symbol in self.watchlist:
            try:
                if self.check_vsa_shakeout(symbol):
                    results.append(symbol)
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")

        if results:
            msg = "🏹 **SWING TRADING ALERTS (VSA)**\n\n"
            msg += "The following stocks show a **Shakeout** pattern (Institutional Trap):\n\n"
            for stock in results:
                msg += f"✅ {stock}\n"
            msg += "\n🔍 *Look for entry on next green candle confirm.*"
            self.telegram.send_message("swing", msg)
            logger.info(f"✅ Swing alerts sent for: {results}")
        else:
            logger.info("🔍 Swing Scan: No VSA Shakeout patterns found today.")

    def check_vsa_shakeout(self, symbol):
        # 1. Fetch historical data
        to_date = datetime.now()
        from_date = to_date - timedelta(days=50)
        
        # We fetch via symbol name
        candles = self.kite.historical_data(self.get_token(symbol), from_date, to_date, "day")
        if not candles: return False
        
        df = pd.DataFrame(candles)
        if len(df) < 20: return False
        
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        avg_volume = df['volume'].tail(20).mean()

        # VSA Logic: Shakeout
        # Price goes below prev low, but closes above it on high volume
        is_shakeout = (last_candle['low'] < prev_candle['low']) and \
                      (last_candle['close'] > prev_candle['low']) and \
                      (last_candle['volume'] > 1.3 * avg_volume)
        
        return is_shakeout

    def get_token(self, symbol):
        """Helper to get instrument token from symbol"""
        # Note: In a production setup, you'd load this from your tokens.json
        quote = self.kite.quote(symbol)
        return quote[symbol]['instrument_token']

if __name__ == "__main__":
    # Test run logic
    from src.scanner.morning_setup import get_kite_instance
    kite = get_kite_instance()
    if kite:
        agent = SwingAgent(kite)
        agent.run()
