"""
Pattern Detection Engine
Detects trading patterns from market data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class PatternDetector:
    """
    Detect various market patterns
    """
    
    def __init__(self):
        self.version = "2.0"
        logger.info(f"PatternDetector v{self.version} initialized")
    
    def detect_v_pattern(self, data: pd.DataFrame) -> Dict:
        """
        Detect V-Shape Volume Recovery Pattern
        """
        try:
            if len(data) < 10:
                return {'detected': False}
            
            # Get last 10 volumes
            volumes = data['Volume'].values[-10:]
            closes = data['Close'].values[-10:]
            
            # Find volume valley (lowest point in last 5 candles)
            recent_volumes = volumes[-5:]
            valley_idx = np.argmin(recent_volumes)
            
            # Check if volume is increasing after valley
            if valley_idx < 3:  # Valley should be within first 3 of last 5
                after_valley = recent_volumes[valley_idx+1:]
                if len(after_valley) >= 2:
                    # Check if volume is increasing
                    if all(after_valley[i] > after_valley[i-1] for i in range(1, len(after_valley))):
                        # Check if price is moving up
                        valley_price = closes[-5 + valley_idx]
                        current_price = closes[-1]
                        
                        if current_price > valley_price * 1.01:  # At least 1% up
                            strength = min((current_price / valley_price - 1) * 100, 95) / 100
                            
                            return {
                                'detected': True,
                                'pattern': 'V-Shape Volume Recovery',
                                'strength': round(strength, 2),
                                'valley_index': valley_idx,
                                'volume_increase': True,
                                'price_increase': current_price > valley_price
                            }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Error in V-pattern detection: {e}")
            return {'detected': False}
    
    def detect_volume_spike(self, data: pd.DataFrame, threshold: float = 2.0) -> Dict:
        """
        Detect volume spike patterns
        """
        try:
            if len(data) < 20:
                return {'detected': False}
            
            current_volume = data['Volume'].iloc[-1]
            avg_volume = data['Volume'].iloc[-20:].mean()
            ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if ratio > threshold:
                return {
                    'detected': True,
                    'pattern': 'Volume Spike',
                    'ratio': round(ratio, 2),
                    'strength': min(ratio / 3, 0.95)
                }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Error in volume spike detection: {e}")
            return {'detected': False}
    
    def detect_support_bounce(self, data: pd.DataFrame) -> Dict:
        """
        Detect bounce from support level
        """
        try:
            if len(data) < 20:
                return {'detected': False}
            
            # Find recent low
            recent_low = data['Low'].iloc[-20:].min()
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2]
            
            # Check if we're near support and bouncing
            near_support = current_price <= recent_low * 1.02
            bouncing = current_price > prev_price
            
            if near_support and bouncing:
                return {
                    'detected': True,
                    'pattern': 'Support Bounce',
                    'support_level': round(recent_low, 2),
                    'strength': 0.75
                }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Error in support detection: {e}")
            return {'detected': False}
    
    def detect_resistance_breakout(self, data: pd.DataFrame) -> Dict:
        """
        Detect breakout above resistance
        """
        try:
            if len(data) < 20:
                return {'detected': False}
            
            # Find recent high
            recent_high = data['High'].iloc[-20:].max()
            current_price = data['Close'].iloc[-1]
            
            # Check for breakout with volume
            volume_ratio = data['Volume'].iloc[-1] / data['Volume'].iloc[-20:].mean()
            
            if current_price > recent_high and volume_ratio > 1.5:
                return {
                    'detected': True,
                    'pattern': 'Resistance Breakout',
                    'resistance_level': round(recent_high, 2),
                    'volume_ratio': round(volume_ratio, 2),
                    'strength': min(0.7 + volume_ratio/10, 0.95)
                }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Error in breakout detection: {e}")
            return {'detected': False}
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:
        """
        Complete analysis of a symbol
        """
        if data is None or data.empty:
            return None
        
        # Run all pattern detections
        patterns = []
        
        # V-Pattern
        v_pattern = self.detect_v_pattern(data)
        if v_pattern['detected']:
            patterns.append(v_pattern)
        
        # Volume Spike
        spike = self.detect_volume_spike(data)
        if spike['detected']:
            patterns.append(spike)
        
        # Support Bounce
        bounce = self.detect_support_bounce(data)
        if bounce['detected']:
            patterns.append(bounce)
        
        # Resistance Breakout
        breakout = self.detect_resistance_breakout(data)
        if breakout['detected']:
            patterns.append(breakout)
        
        if not patterns:
            return None
        
        # Get best pattern (highest strength)
        best_pattern = max(patterns, key=lambda x: x.get('strength', 0))
        
        return {
            'symbol': symbol,
            'time': datetime.now().strftime('%H:%M IST'),
            'date': datetime.now().strftime('%d %b %Y'),
            'price': round(data['Close'].iloc[-1], 2),
            'patterns': patterns,
            'primary_pattern': best_pattern['pattern'],
            'strength': best_pattern.get('strength', 0.7),
            'volume_ratio': round(data['Volume'].iloc[-1] / data['Volume'].iloc[-20:].mean(), 2)
        }
