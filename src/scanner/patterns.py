import logging
import pandas as pd
from kiteconnect import KiteConnect
import pyotp
import time
import os
import json

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmkarAutomation")

class OmkarScannerV3:
    def __init__(self, api_key, api_secret, totp_secret):
        self.kite = KiteConnect(api_key=api_key)
        self.api_secret = api_secret
        self.totp_secret = totp_secret
        self.sma_period = 15
        self.min_quiet_days = 6

    def auto_login(self):
        """Automated authentication using TOTP"""
        try:
            # Note: For full automation in GitHub Actions, you'd usually use 
            # a pre-generated access_token or a headless login flow.
            # This follows your current TOTP structure.
            totp = pyotp.TOTP(self.totp_secret).now()
            logger.info(f"System generated TOTP: {totp}")
            # Placeholder for your specific session generation logic
            # session = self.kite.generate_session(request_token, api_secret=self.api_secret)
            # self.kite.set_access_token(session["access_token"])
        except Exception as e:
            logger.error(f"Login failed: {e}")

    def fetch_data(self, token):
        """Fetches daily data for the last 40 days"""
        to_date = pd.Timestamp.now()
        from_date = to_date - pd.Timedelta(days=40)
        return pd.DataFrame(self.kite.historical_data(token, from_date, to_date, "day"))

    def detect_volume_pattern(self, df):
        """
        Requirement:
        1. Volume must be BELOW 15 SMA for at least 6 consecutive days.
        2. Current Volume must cross ABOVE 15 SMA.
        """
        if len(df) < 20: return None
        
        # Calculate Volume SMA
        df['vol_sma'] = df['volume'].rolling(window=self.sma_period).mean()
        
        # 1. Check previous 6 days (Consolidation)
        # We look at index -7 up to -2
        previous_days = df.iloc[-(self.min_quiet_days + 1):-1]
        quiet_phase = all(previous_days['volume'] < previous_days['vol_sma'])
        
        # 2. Check current day (Breakout)
        current_day = df.iloc[-1]
        volume_breakout = current_day['volume'] > current_day['vol_sma']
        
        if quiet_phase and volume_breakout:
            return {
                'current_vol': int(current_day['volume']),
                'avg_vol': int(current_day['vol_sma']),
                'surge_ratio': round(current_day['volume'] / current_day['vol_sma'], 2)
            }
        return None

    def run(self):
        """Main execution loop"""
        # 1. Get F&O List
        instruments = self.kite.instruments("NFO")
        fo_list = [i for i in instruments if i['segment'] == 'NFO-FUT' and i['name'] != '']
        unique_stocks = {s['name']: s['instrument_token'] for s in fo_list}
        
        results = []
        logger.info(f"Starting scan on {len(unique_stocks)} stocks...")

        for name, token in unique_stocks.items():
            try:
                data = self.fetch_data(token)
                pattern = self.detect_volume_pattern(data)
                
                if pattern:
                    pattern['symbol'] = name
                    pattern['price'] = data.iloc[-1]['close']
                    results.append(pattern)
                    logger.info(f"MATCH: {name} found with {pattern['surge_ratio']}x volume")
                
                time.sleep(0.1) # Rate limiting
            except Exception:
                continue

        # --- EXPORTING RESULTS FOR FURTHER QUERIES ---
        df_results = pd.DataFrame(results)
        
        # 1. Save to CSV (Best for other scripts to read)
        df_results.to_csv("volume_scan_results.csv", index=False)
        
        # 2. Save to JSON (Best for web/apps)
        with open("highlights.json", "w") as f:
            json.dump(results, f, indent=4)

        # 3. Output to GitHub Summary (Visible on your dashboard)
        if not df_results.empty:
            summary_table = df_results[['symbol', 'price', 'surge_ratio']].to_markdown(index=False)
            with open(os.environ.get('GITHUB_STEP_SUMMARY', 'summary.md'), 'a') as f:
                f.write(f"### 🎯 Volume Crossover Results ({pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')})\n")
                f.write(summary_table)
        
        return results

# To run automatically in your GitHub Action:
if __name__ == "__main__":
    # Pull credentials from GitHub Secrets
    scanner = OmkarScannerV3(
        api_key=os.getenv("KITE_API_KEY"),
        api_secret=os.getenv("KITE_API_SECRET"),
        totp_secret=os.getenv("KITE_TOTP_SECRET")
    )
    # Note: Ensure your auto_login handles the access_token correctly for GitHub
    scanner.run()
