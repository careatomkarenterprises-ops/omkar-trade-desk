import os
import logging
import pandas as pd
import pyotp
import time
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class ZerodhaFetcher:
    def __init__(self):
        # Load all credentials from GitHub Secrets
        self.api_key = os.getenv('ZERODHA_API_KEY')
        self.api_secret = os.getenv('ZERODHA_API_SECRET')
        self.user_id = os.getenv('ZERODHA_USER_ID')
        self.password = os.getenv('ZERODHA_PASSWORD')
        self.totp_secret = os.getenv('ZERODHA_TOTP_SECRET')
        
        # Start Automated Login to get the Access Token
        logger.info("Attempting Automated Login via TOTP...")
        self.access_token = self.get_automated_access_token()
        
        if not self.access_token:
            logger.error("Failed to generate Access Token!")
            raise ValueError("Auto-Login failed")

        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)
        
        os.makedirs('data', exist_ok=True)
        self.cache_file = 'data/zerodha_instruments.csv'
        self.load_instruments()
        logger.info("✅ ZerodhaFetcher initialized (Auto-Login Successful)")

    def get_automated_access_token(self):
        """mimics human login to grab access token"""
        options = Options()
        options.add_argument("--headless") # Runs without a visible window
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            kite = KiteConnect(api_key=self.api_key)
            driver.get(kite.login_url())
            
            wait = WebDriverWait(driver, 15)
            # Login
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))).send_keys(self.user_id)
            driver.find_element(By.XPATH, "//input[@type='password']").send_keys(self.password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # 2FA / TOTP Generation
            totp = pyotp.TOTP(self.totp_secret.replace(" ", ""))
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))).send_keys(totp.now())
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Wait for redirect and extract token
            time.sleep(5)
            request_token = driver.current_url.split("request_token=")[1].split("&")[0]
            
            # Exchange for final access token
            session = kite.generate_session(request_token, api_secret=self.api_secret)
            return session["access_token"]
            
        except Exception as e:
            logger.error(f"❌ Auto-Login Error: {e}")
            return None
        finally:
            driver.quit()

    # (Keep your existing get_historical_data and load_instruments methods here)
