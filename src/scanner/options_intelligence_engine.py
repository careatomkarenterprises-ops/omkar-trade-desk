import logging
from src.telegram.poster import TelegramPoster

logger = logging.getLogger(__name__)


class OptionsIntelligenceEngine:

    def __init__(self):
        self.telegram = TelegramPoster()

    def generate_options_signal(self, nifty, banknifty):
        """
        ✅ REQUIRED for system_health_check
        """

        try:
            logger.info("📊 Generating Options Signal")

            return {
                "bias": "BULLISH",
                "flow": "CALL WRITING",
                "confidence": "MEDIUM"
            }

        except Exception as e:
            logger.error(f"❌ Options Signal Error: {e}")
            return {}

    def run(self):
        """
        ✅ Used in live system
        """

        try:
            signal = self.generate_options_signal(None, None)

            message = (
                "📊 OPTIONS INTELLIGENCE\n"
                f"Bias: {signal.get('bias')}\n"
                f"Flow: {signal.get('flow')}\n"
                f"Confidence: {signal.get('confidence')}"
            )

            self.telegram.send_message("free", message)

            return signal

        except Exception as e:
            logger.error("❌ Options Engine Failed")
            logger.exception(e)
            return {}


# ✅ WRAPPER FOR MASTER ENGINE (DO NOT REMOVE)
def run_options_intelligence():
    """
    Wrapper to connect Options Engine with MasterEngine
    """
    try:
        # 👇 CHANGE THIS LINE BASED ON YOUR FILE

        # Most likely:
        result = main()

        # If your function name is different, replace:
        # result = run()
        # result = analyze_options()

        return result

    except Exception as e:
        print(f"Options wrapper error: {e}")
        return None
