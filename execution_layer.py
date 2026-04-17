"""
OMKAR TRADE DESK - PRODUCTION EXECUTION LAYER (STABLE + DEBUG)
"""

import sys
import os
import logging
from datetime import datetime

# ---------------- PATH FIX ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("EXECUTION_LAYER")

# ---------------- IMPORT CONTROLLER ----------------
try:
    from src.scanner.system_controller import SystemController
except Exception as e:
    logger.critical("❌ IMPORT FAILED: system_controller not loading")
    logger.exception(e)
    SystemController = None


# ---------------- PREFLIGHT CHECK ----------------
def preflight_check():

    logger.info("🧪 Running Preflight System Check...")

    required_files = [
        "src/scanner/data_fetcher.py",
        "src/scanner/patterns.py",
        "src/scanner/global_market_engine.py",
        "src/scanner/system_controller.py",
        "src/scanner/full_market_scanner.py"
    ]

    missing = []

    for file in required_files:
        full_path = os.path.join(BASE_DIR, file)
        if not os.path.exists(full_path):
            missing.append(file)

    if missing:
        logger.error(f"❌ Missing Files: {missing}")
        return False

    logger.info("✅ Preflight Check Passed")
    return True


# ---------------- MAIN EXECUTION ----------------
def main():

    logger.info("🚀 OMKAR TRADE DESK STARTED")
    logger.info(f"🕒 Time: {datetime.now()}")

    if not preflight_check():
        logger.critical("❌ SYSTEM STOPPED - FILE ISSUE")
        return

    if SystemController is None:
        logger.critical("❌ SYSTEM STOPPED - CONTROLLER ISSUE")
        return

    try:
        controller = SystemController()
        controller.run()
        logger.info("✅ SYSTEM EXECUTION COMPLETED")

    except Exception as e:
        logger.critical("❌ SYSTEM CRASH DETECTED")
        logger.exception(e)


if __name__ == "__main__":
    main()
