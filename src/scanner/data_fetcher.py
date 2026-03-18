"""
Data Fetcher - Uses Zerodha API first, falls back to Yahoo Finance
"""

import os
import logging
import pandas as pd
from datetime import datetime
from typing import Optional, Dict
import time

from src.scanner.zerodha_fetcher import ZerodhaFetcher
import yfinance as yf

logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Fetch market data - Zerodha first, Yahoo as fallback
    """
    
    def __init__(self):
        self.use_zerodha = False
        self.zerodha = None
        
        # Try to initialize Zerodha (will fail if credentials missing)
        try:
            self.zerodha = ZerodhaFetcher()
            self.use_zerodha = True
            logger.info("✅ Using Zerodha API for market data")
        except Exception as e:
            logger.warning(f"⚠️ Zerodha not available: {e}")
            logger.info("Falling back to Yahoo Finance")
            self.use_zerodha = False
        
        # Yahoo fallback settings
        self.yahoo_delay = 1.0
        self.max_retries = 3
        
        # Symbol mappings for Yahoo (only used as fallback)
        self.nifty_stocks = {
            'RELIANCE': 'RELIANCE.NS',
            'TCS': 'TCS.NS',
            'HDFCBANK': 'HDFCBANK.NS',
            'INFY': 'INFY.NS',
            'ICICIBANK': 'ICICIBANK.NS',
        }
    
    def get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get stock data - Zerodha first, then Yahoo"""
        
        # Try Zerodha first
        if self.use_zerodha:
            try:
                # Get 5 days of 15-min data
                df = self.zerodha.get_historical_data(symbol, interval="15minute", days=5)
                if df is not None and not df.empty:
                    logger.info(f"✅ Got {symbol} data from Zerodha")
                    return df
            except Exception as e:
                logger.warning(f"Zerodha failed for {symbol}, trying Yahoo: {e}")
        
        # Fallback to Yahoo
        return self._get_yahoo_data(symbol)
    
    def _get_yahoo_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Fallback to Yahoo Finance"""
        try:
            # Get Yahoo symbol
            if symbol in self.nifty_stocks:
                yahoo_symbol = self.nifty_stocks[symbol]
            else:
                yahoo_symbol = f"{symbol}.NS" if not symbol.endswith('.NS') else symbol
            
            time.sleep(self.yahoo_delay)
            
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period="5d", interval="15m")
            
            if not data.empty:
                logger.info(f"✅ Got {symbol} from Yahoo (fallback)")
                return data
            else:
                logger.warning(f"No Yahoo data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Yahoo error for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get only current price (fastest)"""
        if self.use_zerodha:
            try:
                ltp_dict = self.zerodha.get_ltp([symbol])
                if symbol in ltp_dict:
                    return ltp_dict[symbol]
            except:
                pass
        
        # Fallback to getting full data and extracting price
        data = self.get_stock_data(symbol)
        if data is not None and not data.empty:
            return data['Close'].iloc[-1]
        return None
