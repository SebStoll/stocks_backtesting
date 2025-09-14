"""
RSI (Relative Strength Index) Strategy.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class RSIStrategy(BaseStrategy):
    """
    RSI-based trading strategy.
    
    Buys when RSI is oversold (< oversold_threshold).
    Sells when RSI is overbought (> overbought_threshold).
    """
    
    def __init__(
        self,
        period: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
        symbol: str = 'SYMBOL',
        name: Optional[str] = None
    ):
        """
        Initialize RSI strategy.
        
        Args:
            period: RSI calculation period
            oversold_threshold: RSI level considered oversold
            overbought_threshold: RSI level considered overbought
            symbol: Symbol to trade
            name: Strategy name
        """
        super().__init__(name)
        self.period = period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.symbol = symbol
        
        # Validate parameters
        if oversold_threshold >= overbought_threshold:
            raise ValueError("Oversold threshold must be less than overbought threshold")
        if not (0 <= oversold_threshold <= 100):
            raise ValueError("Oversold threshold must be between 0 and 100")
        if not (0 <= overbought_threshold <= 100):
            raise ValueError("Overbought threshold must be between 0 and 100")
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """
        Calculate RSI indicator.
        
        Args:
            prices: Price series
            
        Returns:
            RSI series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        Generate trading signals based on RSI.
        
        Args:
            data: Historical data up to current point
            
        Returns:
            Dictionary mapping symbol to signal
        """
        if len(data) < self.period + 1:
            return {self.symbol: 'HOLD'}
        
        # Calculate RSI
        rsi = self.calculate_rsi(data['close'])
        current_rsi = rsi.iloc[-1]
        
        if pd.isna(current_rsi):
            return {self.symbol: 'HOLD'}
        
        # Generate signals
        if current_rsi < self.oversold_threshold:
            return {self.symbol: 'BUY'}
        elif current_rsi > self.overbought_threshold:
            return {self.symbol: 'SELL'}
        else:
            return {self.symbol: 'HOLD'}
    
    def get_parameters(self) -> Dict[str, any]:
        """Get strategy parameters."""
        return {
            'period': self.period,
            'oversold_threshold': self.oversold_threshold,
            'overbought_threshold': self.overbought_threshold,
            'symbol': self.symbol
        }
    
    def set_parameters(self, **kwargs):
        """Set strategy parameters."""
        if 'period' in kwargs:
            self.period = kwargs['period']
        if 'oversold_threshold' in kwargs:
            self.oversold_threshold = kwargs['oversold_threshold']
        if 'overbought_threshold' in kwargs:
            self.overbought_threshold = kwargs['overbought_threshold']
        if 'symbol' in kwargs:
            self.symbol = kwargs['symbol']
        
        # Validate parameters
        if self.oversold_threshold >= self.overbought_threshold:
            raise ValueError("Oversold threshold must be less than overbought threshold")
        if not (0 <= self.oversold_threshold <= 100):
            raise ValueError("Oversold threshold must be between 0 and 100")
        if not (0 <= self.overbought_threshold <= 100):
            raise ValueError("Overbought threshold must be between 0 and 100")
