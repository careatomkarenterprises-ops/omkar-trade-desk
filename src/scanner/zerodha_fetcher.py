import os
import logging
import pandas as pd
import pyotp
import time
import pickle
import zipfile
import urllib.request
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
        
        # Validate all credentials are present
        missing = []
        if not self.api_key: missing.append("ZERODHA_API_KEY")
        if not self.api_secret: missing.append("ZERODHA_API_SECRET")
        if not self.user_id: missing.append("ZERODHA_USER_ID")
        if not self.password: missing.append("ZERODHA_PASSWORD")
        if not self.totp_secret: missing.append("ZERODHA_TOTP_SECRET")
        
        if missing:
            logger.error(f"Missing credentials: {', '.join(missing)}")
            raise ValueError(f"Missing Zerodha credentials: {', '.join(missing)}")
        
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
            logger.info("✅ Auto-Login successful!")
        else:
            logger.error("❌ Auto-Login failed. Check your Credentials/TOTP Secret.")
            raise ValueError("Could not connect to Zerodha")

    def _download_chromedriver(self):
        """Manually download and extract ChromeDriver"""
        try:
            # ChromeDriver version for Chrome 146
            version = "146.0.7680.165"
            download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chromedriver-linux64.zip"
            
            # Create directory
            driver_dir = os.path.expanduser("~/.chromedriver")
            os.makedirs(driver_dir, exist_ok=True)
            
            chromedriver_path = os.path.join(driver_dir, "chromedriver")
            
            # Check if already downloaded
            if os.path.exists(chromedriver_path):
                logger.info(f"ChromeDriver already exists at {chromedriver_path}")
                return chromedriver_path
            
            # Download zip file
            zip_path = os.path.join(driver_dir, "chromedriver.zip")
            logger.info(f"Downloading ChromeDriver from {download_url}...")
            
            urllib.request.urlretrieve(download_url, zip_path)
            logger.info("Download complete, extracting...")
            
            # Extract zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(driver_dir)
            
            # Find the chromedriver binary in extracted folder
            extracted_dir = os.path.join(driver_dir, "chromedriver-linux64")
            extracted_binary = os.path.join(extracted_dir, "chromedriver")
            
            if os.path.exists(extracted_binary):
                # Move to final location
                import shutil
                shutil.move(extracted_binary, chromedriver_path)
                # Clean up
                os.remove(zip_path)
                shutil.rmtree(extracted_dir)
                logger.info(f"✅ ChromeDriver installed at {chromedriver_path}")
            else:
                raise Exception("Binary not found after extraction")
            
            # Make executable
            os.chmod(chromedriver_path, 0o755)
            
            return chromedriver_path
            
        except Exception as e:
            logger.error(f"Failed to download ChromeDriver: {e}")
            return None

    def get_automated_access_token(self):
        """Auto-login to Zerodha using Selenium"""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,720")
        
        driver = None
        try:
            # Download ChromeDriver manually
            chromedriver_path = self._download_chromedriver()
            if not chromedriver_path:
                logger.error("Could not download ChromeDriver")
                return None
            
            logger.info(f"✅ Using ChromeDriver at: {chromedriver_path}")
            
            # Setup service
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            
            kite = KiteConnect(api_key=self.api_key)
            login_url = kite.login_url()
            logger.info(f"Navigating to login page...")
            driver.get(login_url)
            
            wait = WebDriverWait(driver, 20)
            
            # Step 1: Enter User ID
            logger.info("Entering User ID...")
            userid_input = wait.until(EC.presence_of_element_located((By.ID, "userid")))
            userid_input.clear()
            userid_input.send_keys(self.user_id)
            
            # Step 2: Enter Password
            logger.info("Entering Password...")
            password_input = driver.find_element(By.ID, "password")
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Step 3: Click Login button
            logger.info("Clicking Login button...")
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Step 4: Wait for 2FA page and enter TOTP
            time.sleep(3)
            logger.info("Waiting for 2FA input...")
            
            try:
                # Look for TOTP input field
                totp_input = wait.until(EC.presence_of_element_located((By.ID, "twofa")))
                totp = pyotp.TOTP(self.totp_secret.replace(" ", ""))
                otp_code = totp.now()
                logger.info(f"Entering TOTP: {otp_code}")
                totp_input.clear()
                totp_input.send_keys(otp_code)
                
                # Submit TOTP
                submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()
                time.sleep(3)
            except Exception as e:
                logger.warning(f"TOTP entry issue: {e}")
            
            # Step 5: Wait for redirect and capture request_token
            time.sleep(5)
            current_url = driver.current_url
            logger.info(f"Redirected to: {current_url[:100]}...")
            
            if "request_token=" not in current_url:
                driver.save_screenshot("data/login_failed.png")
                logger.error(f"Login failed. No request_token in URL")
                return None
                
            request_token = current_url.split("request_token=")[1].split("&")[0]
            logger.info(f"✅ Got request_token: {request_token[:20]}...")
            
            # Step 6: Exchange for access token
            session = kite.generate_session(request_token, api_secret=self.api_secret)
            logger.info("✅ Access token generated successfully!")
            return session["access_token"]
            
        except Exception as e:
            logger.error(f"Auto-Login Error: {e}")
            if driver:
                driver.save_screenshot("data/login_error.png")
            return None
        finally:
            if driver:
                driver.quit()

    def _save_session(self):
        """Save session to disk for reuse"""
        session_data = {
            'access_token': self.access_token, 
            'api_key': self.api_key,
            'created_at': datetime.now().isoformat()
        }
        with open(self.token_file, 'wb') as f:
            pickle.dump(session_data, f)
        logger.info(f"✅ Session saved to {self.token_file}")

    def _load_session(self) -> bool:
        """Load and validate existing session"""
        if not os.path.exists(self.token_file):
            return False
        try:
            with open(self.token_file, 'rb') as f:
                data = pickle.load(f)
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(data['access_token'])
            # Validate token by making a test call
            self.kite.profile()
            logger.info("✅ Session valid")
            return True
        except Exception as e:
            logger.warning(f"Session invalid: {e}")
            return False

    def refresh_if_needed(self):
        """Check if token is still valid"""
        try:
            if self.kite:
                self.kite.profile()
        except Exception:
            logger.warning("Token may be expired, will refresh on next call")
            self._initialize_connection()

    def load_instruments(self):
        """Load instrument list (updated daily)"""
        try:
            self.refresh_if_needed()
            
            if os.path.exists(self.cache_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
                if mod_time.date() == datetime.now().date():
                    logger.info("Using cached instruments from today")
                    return
            
            logger.info("Fetching fresh instrument list from Zerodha...")
            instruments = self.kite.instruments()
            df = pd.DataFrame(instruments)
            df.to_csv(self.cache_file, index=False)
            logger.info(f"✅ Loaded {len(df)} instruments")
            
        except Exception as e:
            logger.error(f"Error loading instruments: {e}")

    def get_instrument_token(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        """Get instrument token for a symbol"""
        try:
            self.refresh_if_needed()
            
            cache_key = f"{exchange}:{symbol}"
            if cache_key in self.instrument_cache:
                return self.instrument_cache[cache_key]
            
            df = pd.read_csv(self.cache_file)
            match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == symbol)]
            
            if match.empty and exchange == "NSE":
                match = df[(df['exchange'] == exchange) & (df['tradingsymbol'] == f"{symbol}EQ")]
            
            if not match.empty:
                token = str(match.iloc[0]['instrument_token'])
                self.instrument_cache[cache_key] = token
                return token
            
            logger.warning(f"No token found for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting token for {symbol}: {e}")
            return None

    def get_historical_data(self, symbol: str, interval: str = "day", days: int = 45) -> Optional[pd.DataFrame]:
        """Get historical candle data"""
        try:
            self.refresh_if_needed()
            
            token = self.get_instrument_token(symbol)
            if not token:
                return None
            
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            candles = self.kite.historical_data(
                int(token), 
                from_date.strftime("%Y-%m-%d %H:%M:%S"), 
                to_date.strftime("%Y-%m-%d %H:%M:%S"), 
                interval
            )
            
            if candles:
                df = pd.DataFrame(candles)
                df = df.rename(columns={
                    'date': 'Date', 'open': 'Open', 'high': 'High',
                    'low': 'Low', 'close': 'Close', 'volume': 'Volume'
                })
                df.set_index('Date', inplace=True)
                logger.info(f"✅ Got {len(df)} days of data for {symbol}")
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Data error for {symbol}: {e}")
            return None

    def get_ltp(self, symbols: List[str]) -> Dict:
        """Get last traded prices for multiple symbols"""
        try:
            self.refresh_if_needed()
            formatted = [f"NSE:{s}" for s in symbols]
            ltp_data = self.kite.ltp(formatted)
            
            result = {}
            for sym in symbols:
                key = f"NSE:{sym}"
                if key in ltp_data:
                    result[sym] = ltp_data[key]['last_price']
            return result
            
        except Exception as e:
            logger.error(f"Error fetching LTP: {e}")
            return {}

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol"""
        try:
            self.refresh_if_needed()
            quotes = self.kite.quote([f"NSE:{symbol}"])
            
            if quotes and f"NSE:{symbol}" in quotes:
                quote = quotes[f"NSE:{symbol}"]
                return {
                    'symbol': symbol,
                    'last_price': quote['last_price'],
                    'volume': quote.get('volume', 0),
                    'open': quote['ohlc']['open'],
                    'high': quote['ohlc']['high'],
                    'low': quote['ohlc']['low'],
                    'close': quote['ohlc']['close'],
                    'timestamp': quote['timestamp'],
                    'source': 'zerodha'
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching quote: {e}")
            return None
