import os
import logging
import pandas as pd
import pyotp
import time
import pickle
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class ZerodhaFetcher:
    def __init__(self):
        # Load credentials from GitHub Secrets
        self.api_key = os.getenv('ZERODHA_API_KEY')
        self.api_secret = os.getenv('ZERODHA_API_SECRET')
        self.user_id = os.getenv('ZERODHA_USER_ID')
        self.password = os.getenv('ZERODHA_PASSWORD')
        self.totp_secret = os.getenv('ZERODHA_TOTP_SECRET')
        self.token_file = 'data/zerodha_session.pkl'
        
        os.makedirs('data', exist_ok=True)
        self.kite = None
        self.access_token = None
        
        # Start connection process
        self._initialize_connection()
        
        self.cache_file = 'data/zerodha_instruments.csv'
        self.instrument_cache = {}
        self.load_instruments()
        logger.info("✅ ZerodhaFetcher fully initialized and automated")

    def _initialize_connection(self):
        """Checks if old session works, otherwise logs in automatically"""
        if self._load_session():
            logger.info("✅ Reusing existing session")
            return

        logger.info("🔄 Session expired. Starting Auto-Login engine...")
        self.access_token = self.get_automated_access_token()
        
        if self.access_token:
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            self._save_session()
        else:
            logger.error("❌ Auto-Login failed. Check your Credentials/TOTP Secret.")
            raise ValueError("Could not connect to Zerodha")

    def get_automated_access_token(self):
        """Fixed version with deep-search for the correct chromedriver binary on Linux"""
        options = Options()
        options.add_argument("--headless") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = "/usr/bin/google-chrome"
        
        try:
            # 1. Install and get the initial path
            install_path = ChromeDriverManager().install()
            
            # 2. DEEP SEARCH: Look for the actual 'chromedriver' binary
            exec_path = None
            # Search in the directory where webdriver-manager downloaded the files
            search_dir = os.path.dirname(install_path)
            
            for root, dirs, files in os.walk(search_dir):
                if "chromedriver" in files:
                    temp_path = os.path.join(root, "chromedriver")
                    # Ignore license/notice files and ensure it's a file, not a folder
                    if os.path.isfile(temp_path) and "THIRD_PARTY" not in temp_path:
                        exec_path = temp_path
                        break
            
            if not exec_path:
                logger.error("Could not find the actual chromedriver binary.")
                return None

            logger.info(f"🚀 Success! Found binary at: {exec_path}")
            
            # Ensure the file has execution permissions on Linux
            os.chmod(exec_path, 0o755)

            service = Service(executable_path=exec_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            kite = KiteConnect(api_key=self.api_key)
            driver.get(kite.login_url())
            wait = WebDriverWait(driver, 20)
            
            # Step 1: Login ID & Password
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))).send_keys(self.user_id)
            driver.find_element(By.XPATH, "//input[@type='password']").send_keys(self.password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Step 2: Enter TOTP
            totp = pyotp.TOTP(self.totp_secret.replace(" ", ""))
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))).send_keys(totp.now())
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Step 3: Wait and grab token from URL
            time.sleep(5)
            current_url = driver.current_url
            if "request_token=" not in current_url:
                logger.error(f"Login failed. Current URL: {current_url}")
                return None
                
            request_token = current_url.split("request_token=")[1].split("&")[0]
            
            # Step 4: Final handshake
            session = kite.generate_session(request_token, api_secret=self.api_secret)
            return session["access_token"]
            
        except Exception as e:
            logger.error(f"Auto-Login Error: {e}")
            return None
        finally:
            if 'driver' in locals():
                driver.quit()

    def _save_session(self):
        session_data = {'access_token': self.access_token, 'api_key': self.api_key}
        with open(self.token_file, 'wb') as f:
            pickle.dump(session_data, f)

    def _load_session(self) -> bool:
        if not os.path.exists(self.token_file): return False
        try:
            with open(self.token_file, 'rb') as f:
                data = pickle.load(f)
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(data['access_token'])
            self.kite.profile() 
            return True
        except: return False

    def load_instruments(self):
        try:
            if os.path.exists(self.cache_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
                if mod_time.date() == datetime.now().date(): return
            instruments = self.kite.instruments()
            pd.DataFrame(instruments).to_csv(self.cache_file, index=False)
        except Exception as e:
            logger.error(f"Error loading instruments: {e}")

    def get_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        try:
            cache_key = f"{exchange}:{symbol}"
            if cache_key in self.instrument_cache: return self.instrument_cache[cache_key]
            df = pd.read_csv(self.cache_file)
            match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == symbol)]
            if match.empty and exchange == "NSE":
                match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == f"{symbol}EQ")]
            if not match.empty:
                token = str(match.iloc[0]['instrument_token'])
                self.instrument_cache[cache_key] = token
                return token
            return None
        except: return None

    def get_historical_data(self, symbol: str, interval: str = "day", days: int = 45) -> Optional[pd.DataFrame]:
        try:
            token = self.get_instrument_token(symbol)
            if not token: return None
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            candles = self.kite.historical_data(int(token), from_date.strftime("%Y-%m-%d %H:%M:%S"), to_date.strftime("%Y-%m-%d %H:%M:%S"), interval)
            if candles:
                df = pd.DataFrame(candles).rename(columns={'date':'Date','open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'})
                df.set_index('Date', inplace=True)
                return df
            return None
        except Exception as e:
            logger.error(f"Data error for {symbol}: {e}")
            return None

    def get_ltp(self, symbols: List[str]) -> Dict:
        try:
            formatted = [f"NSE:{s}" for s in symbols]
            ltp_data = self.kite.ltp(formatted)
            return {s: ltp_data[f"NSE:{s}"]['last_price'] for s in symbols if f"NSE:{s}" in ltp_data}
        except: return {}
