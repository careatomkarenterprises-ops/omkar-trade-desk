"""
OMKAR TRADE DESK - PRODUCTION EXECUTION LAYER
FINAL CLEAN VERSION (LIVE SCANNER ENABLED)
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

# ---------------- IMPORT SCANNER ----------------
try:
    from src.scanner.full_market_scanner import run_full_scan
except Exception as e:
    logger.critical(f"❌ IMPORT FAILED: {e}")
    run_full_scan = None


# ---------------- PRE-FLIGHT CHECK ----------------
def preflight_check():

    logger.info("🧪 Running Preflight System Check...")

    required_files = [
        "src/scanner/data_fetcher.py",
        "src/scanner/patterns.py",
        "src/scanner/full_market_scanner.py",
        "src/telegram/poster.py"
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

    logger.info("🚀 OMKAR TRADE DESK LIVE SYSTEM STARTED")
    logger.info(f"🕒 Time: {datetime.now()}")

    # STEP 1: Safety Check
    if not preflight_check():
        logger.critical("❌ SYSTEM STOPPED - FILE STRUCTURE ISSUE")
        return

    # STEP 2: Run Scanner
    if run_full_scan is None:
        logger.critical("❌ SYSTEM STOPPED - SCANNER NOT LOADED")
        return

    try:
        results = run_full_scan()
        logger.info(f"✅ Scan Completed | Signals Found: {len(results)}")

    except Exception as e:
        logger.critical(f"❌ SYSTEM FAILURE: {e}")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    main()
