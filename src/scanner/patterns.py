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
        """Detect V-Shape Volume Recovery Pattern"""
        try:
            if len(data) < 10:
                return {'detected': False}
            
            volumes = data['Volume'].values[-10:]
            closes = data['Close'].values[-10:]
            recent_volumes = volumes[-5:]
            valley_idx = np.argmin(recent_volumes)
            
            if valley_idx < 3:
                after_valley = recent_volumes[valley_idx+1:]
                if len(after_valley) >= 2:
                    if all(after_valley[i] > after_valley[i-1] for i in range(1, len(after_valley))):
                        valley_price = closes[-5 + valley_idx]
                        current_price = closes[-1]
                        
                        if current_price > valley_price * 1.005:
                            strength = min((current_price / valley_price - 1) * 100, 95) / 100
                            return {
                                'detected': True,
                                'pattern': 'V-Shape Volume Recovery',
                                'strength': round(strength, 2),
                                'price_increase': True
                            }
            return {'detected': False}
        except Exception as e:
            logger.error(f"Error in V-pattern detection: {e}")
            return {'detected': False}

    def detect_volume_spike(self, data: pd.DataFrame, threshold: float = 1.8) -> Dict:
        """Detect volume spike patterns"""
        try:
            if len(data) < 20: return {'detected': False}
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
            logger.error(f"Error in volume spike: {e}")
            return {'detected': False}

    def detect_support_bounce(self, data: pd.DataFrame) -> Dict:
        """Detect bounce from support level"""
        try:
            if len(data) < 20: return {'detected': False}
            recent_low = data['Low'].iloc[-20:].min()
            current_price = data['Close'].iloc[-1]
            if current_price <= recent_low * 1.015 and current_price > data['Close'].iloc[-2]:
                return {'detected': True, 'pattern': 'Support Bounce', 'strength': 0.75}
            return {'detected': False}
        except Exception as e:
            return {'detected': False}

    def detect_resistance_breakout(self, data: pd.DataFrame) -> Dict:
        """Detect breakout above resistance"""
        try:
            if len(data) < 20: return {'detected': False}
            recent_high = data['High'].iloc[-20:].max()
            current_price = data['Close'].iloc[-1]
            vol_ratio = data['Volume'].iloc[-1] / data['Volume'].iloc[-20:].mean()
            if current_price > recent_high and vol_ratio > 1.5:
                return {'detected': True, 'pattern': 'Resistance Breakout', 'strength': 0.8}
            return {'detected': False}
        except Exception as e:
            return {'detected': False}

    def detect_trend_strength(self, data: pd.DataFrame) -> Dict:
        """Detect trend strength using MAs"""
        try:
            if len(data) < 50: return {'trend': 'neutral', 'strength': 0.5}
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]
            current = data['Close'].iloc[-1]
            if current > sma_20 > sma_50:
                return {'trend': 'bullish', 'strength': 0.8, 'description': 'Strong uptrend'}
            elif current < sma_20 < sma_50:
                return {'trend': 'bearish', 'strength': 0.8, 'description': 'Strong downtrend'}
            return {'trend': 'neutral', 'strength': 0.5, 'description': 'Consolidating'}
        except:
            return {'trend': 'neutral', 'strength': 0.5}

    def analyze(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:
        """Complete analysis of a symbol"""
        if data is None or data.empty: return None
        patterns = []
        
        # Check all patterns
        for func in [self.detect_v_pattern, self.detect_volume_spike, 
                     self.detect_support_bounce, self.detect_resistance_breakout]:
            res = func(data)
            if res['detected']: patterns.append(res)
        
        trend = self.detect_trend_strength(data)
        has_pattern = len(patterns) > 0
        best_p = max(patterns, key=lambda x: x.get('strength', 0)) if has_pattern else {'pattern': 'No Pattern', 'strength': 0.3}

        return {
            'symbol': symbol,
            'price': round(data['Close'].iloc[-1], 2),
            'primary_pattern': best_p['pattern'],
            'strength': best_p['strength'],
            'trend': trend['trend'],
            'has_pattern': has_pattern
        }
