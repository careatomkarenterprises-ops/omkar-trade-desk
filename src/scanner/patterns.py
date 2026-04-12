"""
Pattern Detection Engine - Institutional Silent Accumulation Edition
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PatternDetector:
    def __init__(self):
        self.version = "3.0"
        # Parameters for Institutional Footprint
        self.vol_sma_period = 15      # 15-day Volume SMA
        self.quiet_days = 6           # Days volume must stay below SMA
        self.box_lookback = 6         # Period to determine Support/Resistance
        self.surge_threshold = 1.8    # Volume must be 1.8x the SMA to trigger

    def detect_volume_price_box(self, data: pd.DataFrame) -> Dict:
        """
        Detects 6+ days of quiet volume (below 15 SMA) followed by 
        a price breakout from the 'Box' on high volume.
        """
        try:
            if len(data) < 20:
                return {'detected': False}

            # 1. Calculate 15-day Volume SMA
            data = data.copy()
            data['vol_sma'] = data['volume'].rolling(window=self.vol_sma_period).mean()
            
            # 2. Check the "Quiet Period" (Previous 6 days excluding today)
            # We look at index -7 to -2
            quiet_slice = data.iloc[-(self.quiet_days + 1): -1]
            is_quiet = all(quiet_slice['volume'] < quiet_slice['vol_sma'])

            # 3. Define the "Box" (High/Low of those 6 quiet days)
            resistance = quiet_slice['high'].max()
            support = quiet_slice['low'].min()

            # 4. Check Today's Action (The Trigger)
            current_bar = data.iloc[-1]
            current_close = current_bar['close']
            current_volume = current_bar['volume']
            current_vol_sma = current_bar['vol_sma']

            # Trigger Conditions:
            # - Price breaks above Resistance OR below Support
            # - Volume is significantly higher than the 15 SMA
            breakout = current_close > resistance
            breakdown = current_close < support
            volume_surge = current_volume > (current_vol_sma * self.surge_threshold)

            if (breakout or breakdown) and volume_surge:
                trigger_type = "🚀 BOX BREAKOUT" if breakout else "📉 BOX BREAKDOWN"
                surge_ratio = round(current_volume / current_vol_sma, 2)
                
                return {
                    'detected': True,
                    'trigger': trigger_type,
                    'resistance': round(resistance, 2),
                    'support': round(support, 2),
                    'surge_ratio': surge_ratio,
                    'strength': min(surge_ratio / 3, 1.0) # Normalized score
                }

            return {'detected': False}

        except Exception as e:
            logger.error(f"Pattern Error: {e}")
            return {'detected': False}

    def analyze(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:
        """Main entry point for core.py"""
        if data is None or data.empty:
            return None

        # Run the specific Institutional Scanner
        res = self.detect_volume_price_box(data)
        
        if res['detected']:
            return {
                'symbol': symbol,
                'price': round(data['close'].iloc[-1], 2),
                'has_pattern': True,
                'trigger': res['trigger'],
                'surge_ratio': res['surge_ratio'],
                'resistance': res['resistance'],
                'support': res['support'],
                'strength': res['strength']
            }
        
        return {'symbol': symbol, 'has_pattern': False}
