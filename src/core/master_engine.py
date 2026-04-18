from src.scanner.full_market_scanner import run_full_market_scan
from src.scanner.global_market_engine import run_global_market_analysis
from src.scanner.options_intelligence_engine import run_options_intelligence
from src.telegram.router import route_signal
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MasterEngine:

    def run(self):
        logger.info("🚀 MASTER ENGINE STARTED")

        market_bias = self.get_market_bias()
        options_data = self.get_options_data()
        signals = self.get_signals()

        processed_signals = self.process_signals(signals, market_bias, options_data)

        self.dispatch(processed_signals)

        logger.info("✅ MASTER ENGINE COMPLETED")

    def get_market_bias(self):
        try:
            return run_global_market_analysis()
        except Exception as e:
            logger.error(f"Market bias error: {e}")
            return "NEUTRAL"

    def get_options_data(self):
        try:
            return run_options_intelligence()
        except Exception as e:
            logger.error(f"Options error: {e}")
            return None

    def get_signals(self):
        try:
            return run_full_market_scan()
        except Exception as e:
            logger.error(f"Scanner error: {e}")
            return []

    def process_signals(self, signals, market_bias, options_data):

        final_signals = []

        for signal in signals:

            confidence = self.calculate_confidence(signal, options_data)

            signal["confidence"] = confidence
            signal["market_bias"] = market_bias

            if confidence >= 60:
                final_signals.append(signal)

        return final_signals

    def calculate_confidence(self, signal, options_data):

        score = 0

        if signal.get("volume_spike"):
            score += 25

        if signal.get("pattern"):
            score += 25

        if signal.get("trend"):
            score += 25

        if options_data:
            score += 25

        return score

    def dispatch(self, signals):

        for signal in signals:
            route_signal(signal)
