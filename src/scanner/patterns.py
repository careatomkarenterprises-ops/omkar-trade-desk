"""
Pattern Detection Engine - Volume Price Box (Professional Edition)
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PatternDetector:
    def __init__(self):
        self.version = "3.1"
        self.sma_period = 15
        self.quiet_days = 6
        logger.info(f"PatternDetector v{self.version} initialized with SMA pollution fix")

    def detect_volume_price_box(self, data: pd.DataFrame) -> Dict:
        """
        Logic:
        1. Baseline: 15 SMA calculated PRIOR to the quiet period (No pollution).
        2. Quiet Phase: 6 days where Volume < Baseline.
        3. Explosion: Current Volume > Baseline.
        4. Price: Breakout/Breakdown of 6-day range OR > 50% move.
        """
        try:
            df = data.copy()
            df.columns = [c.lower() for c in df.columns]
            
            # We need at least (15 SMA + 6 Quiet + 1 Trigger) = 22 days minimum
            if len(df) < 25:
                return {'detected': False}

            # --- THE FIX: ISOLATE THE BASELINE ---
            # Extract the 6 quiet days
            quiet_window = df.iloc[-(self.quiet_days + 1):-1]
            
            # Extract the historical data BEFORE those 6 quiet days to calculate SMA
            historical_for_sma = df.iloc[:-(self.quiet_days + 1)]
            
            # Get the last 15 days of that historical data
            baseline_volumes = historical_for_sma['volume'].tail(self.sma_period)
            baseline_sma = baseline_volumes.mean()
            
            if baseline_sma == 0: return {'detected': False}

            # --- VALIDATION ---
            # 1. Was it quiet? (Check against the clean baseline)
            volume_was_quiet = all(quiet_window['volume'] < baseline_sma)
            
            # 2. Is there a spike today?
            current_day = df.iloc[-1]
            volume_spike = current_day['volume'] > baseline_sma
            
            if not (volume_was_quiet and volume_spike):
                return {'detected': False}

            # --- PRICE ACTION BOX ---
            resistance = quiet_window['high'].max()
            support = quiet_window['low'].min()
            range_height = resistance - support
            
            curr_close = current_day['close']
            prev_close = df.iloc[-2]['close'] # Closing price of the last quiet day
            move_dist = abs(curr_close - prev_close)

            # --- TRIGGER DETERMINATION ---
            trigger = None
            if curr_close > resistance:
                trigger = "🚀 BREAKOUT"
            elif curr_close < support:
                trigger = "📉 BREAKDOWN"
            elif move_dist > (range_height * 0.5):
                trigger = "⚡ 50% RANGE MOVE"

            if trigger:
                return {
                    'detected': True,
                    'pattern': 'Volume Price Box',
                    'trigger': trigger,
                    'resistance': round(resistance, 2),
                    'support': round(support, 2),
                    'surge_ratio': round(current_day['volume'] / baseline_sma, 2)
                }
                
            return {'detected': False}

        except Exception as e:
            logger.error(f"Detection Error: {e}")
            return {'detected': False}

    def analyze(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:
        """Entry point for the scanner loop"""
        if data is None or data.empty:
            return None
            
        res = self.detect_volume_price_box(data)
        
        if res['detected']:
            return {
                'symbol': symbol,
                'price': round(data.iloc[-1]['close'] if 'close' in data.columns else data.iloc[-1]['Close'], 2),
                'pattern': res['pattern'],
                'trigger': res['trigger'],
                'surge_ratio': res['surge_ratio'],
                'resistance': res['resistance'],
                'support': res['support'],
                'has_pattern': True
            }
        
        return None
