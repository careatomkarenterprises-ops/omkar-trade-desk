def run(self, symbols, global_data):

    logger.info("🚀 Running Premarket Prediction Engine...")

    # ✅ AUTO SYMBOL FETCH FROM NSE PREOPEN
    if not symbols:
        logger.warning("⚠ No symbols provided, fetching NSE pre-open movers")

        try:
            import requests

            url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }

            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers)

            response = session.get(url, headers=headers)
            data = response.json()

            symbols = [
                item["metadata"]["symbol"]
                for item in data.get("data", [])[:50]
            ]

            logger.info(f"✅ Loaded {len(symbols)} pre-open symbols")

        except Exception as e:
            logger.error(f"❌ NSE Fetch Failed: {e}")
            symbols = ["RELIANCE", "TCS", "INFY"]
