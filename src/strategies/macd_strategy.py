"""
MACD (Moving Average Convergence Divergence) Strategy.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class MACDStrategy(BaseStrategy):
    """
    MACD-based trading strategy.
    
    Buys when MACD line crosses above signal line.
    Sells when MACD line crosses below signal line.
    """
    
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        symbol: str = 'SYMBOL',
        name: Optional[str] = None
    ):
        """
        Initialize MACD strategy.
        
        Args:
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line EMA period
            symbol: Symbol to trade
            name: Strategy name
        """
        super().__init__(name)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.symbol = symbol
        
        # Validate parameters
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")
    
    def calculate_macd(self, prices: pd.Series):
        """
        Calculate MACD indicator.
        
        Args:
            prices: Price series
            
        Returns:
            Tuple of (MACD line, signal line, histogram)
        """
        # Calculate EMAs
        ema_fast = prices.ewm(span=self.fast_period).mean()
        ema_slow = prices.ewm(span=self.slow_period).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = macd_line.ewm(span=self.signal_period).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        Generate trading signals based on MACD.
        
        Args:
            data: Historical data up to current point
            
        Returns:
            Dictionary mapping symbol to signal
        """
        if len(data) < self.slow_period + self.signal_period:
            return {self.symbol: 'HOLD'}
        
        # Calculate MACD
        macd_line, signal_line, histogram = self.calculate_macd(data['close'])
        
        # Get current and previous values
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        
        if len(data) < self.slow_period + self.signal_period + 1:
            return {self.symbol: 'HOLD'}
        
        prev_macd = macd_line.iloc[-2]
        prev_signal = signal_line.iloc[-2]
        
        if pd.isna(current_macd) or pd.isna(current_signal) or pd.isna(prev_macd) or pd.isna(prev_signal):
            return {self.symbol: 'HOLD'}
        
        # Check for crossover
        if (prev_macd <= prev_signal and current_macd > current_signal):
            # MACD crosses above signal - buy signal
            return {self.symbol: 'BUY'}
        elif (prev_macd >= prev_signal and current_macd < current_signal):
            # MACD crosses below signal - sell signal
            return {self.symbol: 'SELL'}
        else:
            return {self.symbol: 'HOLD'}
    
    def get_parameters(self) -> Dict[str, any]:
        """Get strategy parameters."""
        return {
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'signal_period': self.signal_period,
            'symbol': self.symbol
        }
    
    def set_parameters(self, **kwargs):
        """Set strategy parameters."""
        if 'fast_period' in kwargs:
            self.fast_period = kwargs['fast_period']
        if 'slow_period' in kwargs:
            self.slow_period = kwargs['slow_period']
        if 'signal_period' in kwargs:
            self.signal_period = kwargs['signal_period']
        if 'symbol' in kwargs:
            self.symbol = kwargs['symbol']
        
        # Validate parameters
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")
