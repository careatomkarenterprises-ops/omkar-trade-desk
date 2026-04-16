"""
OMKAR TRADE DESK - PRODUCTION EXECUTION LAYER
Single Entry Point for ALL GitHub Workflows
"""

import sys
import os
import logging
from datetime import datetime

# ---------------- SAFE PATH FIX ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("EXECUTION_LAYER")

# ---------------- CORE SYSTEM IMPORT ----------------
try:
    from src.scanner.system_controller import main as run_system
except Exception as e:
    logger.critical(f"❌ IMPORT FAILED: {e}")
    run_system = None


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

    # STEP 1: Safety Check
    if not preflight_check():
        logger.critical("❌ SYSTEM STOPPED - FILE STRUCTURE ISSUE")
        return

    # STEP 2: Run Core System
    if run_system is None:
        logger.critical("❌ SYSTEM STOPPED - CORE ENGINE NOT LOADED")
        return

    try:
        run_system()
        logger.info("✅ SYSTEM EXECUTION COMPLETED SUCCESSFULLY")

    except Exception as e:
        logger.critical(f"❌ SYSTEM CRASH: {e}")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    main()
