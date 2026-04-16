import logging

logger = logging.getLogger(__name__)


class SystemController:

    def __init__(self):
        self.health_status = {}

    def validate(self, fetcher, detector):

        logger.info("🧠 Running System Validation Gate...")

        try:
            # Test Data Layer
            data = fetcher.get_stock_data("RELIANCE")

            if data is None or data.empty:
                self.health_status["data"] = False
                return False

            # Test Pattern Layer
            result = detector.analyze("RELIANCE", data)

            if result is None:
                self.health_status["pattern"] = False
                return False

            self.health_status["data"] = True
            self.health_status["pattern"] = True

            logger.info("✅ System Validation PASSED")
            return True

        except Exception as e:
            logger.error(f"❌ System Validation FAILED: {e}")
            return False
