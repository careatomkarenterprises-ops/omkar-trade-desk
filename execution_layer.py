"""
OMKAR TRADE DESK - PRODUCTION EXECUTION LAYER
Single Entry Point for ALL GitHub Workflows
"""

import sys
import os
import logging
from datetime import datetime

# ---------------- SAFE PATH FIX ----------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("EXECUTION_LAYER")

# ---------------- CORE SYSTEM IMPORT ----------------
from src.scanner.system_controller import main as run_system


# ---------------- PRE-FLIGHT CHECK ----------------
def preflight_check():

    logger.info("🧪 Running Preflight System Check...")

    required_files = [
        "src/scanner/data_fetcher.py",
        "src/scanner/patterns.py",
        "src/scanner/global_market_engine.py",
        "src/scanner/options_intelligence_engine.py",
        "src/scanner/telegram_report_engine.py",
        "src/scanner/system_controller.py"
    ]

    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"❌ Missing file: {file}")
            return False

    logger.info("✅ Preflight Check Passed")
    return True


# ---------------- MAIN EXECUTION ----------------
def main():

    logger.info("🚀 OMKAR TRADE DESK STARTED")
    logger.info(f"🕒 Time: {datetime.now()}")

    # STEP 1: Safety Check
    if not preflight_check():
        logger.critical("❌ SYSTEM STOPPED - MISSING FILES")
        return

    try:
        # STEP 2: Run Core System
        run_system()
        logger.info("✅ SYSTEM EXECUTION COMPLETED SUCCESSFULLY")

    except Exception as e:
        logger.critical(f"❌ SYSTEM CRASH: {e}")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    main()
