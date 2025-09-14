"""
Moving Average Crossover Strategy.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class MovingAverageStrategy(BaseStrategy):
    """
    Simple moving average crossover strategy.
    
    Buys when short MA crosses above long MA.
    Sells when short MA crosses below long MA.
    """
    
    def __init__(
        self,
        short_window: int = 20,
        long_window: int = 50,
        symbol: str = 'SYMBOL',
        name: Optional[str] = None
    ):
        """
        Initialize moving average strategy.
        
        Args:
            short_window: Short moving average window
            long_window: Long moving average window
            symbol: Symbol to trade
            name: Strategy name
        """
        super().__init__(name)
        self.short_window = short_window
        self.long_window = long_window
        self.symbol = symbol
        
        # Validate parameters
        if short_window >= long_window:
            raise ValueError("Short window must be less than long window")
    
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        Generate trading signals based on moving average crossover.
        
        Args:
            data: Historical data up to current point
            
        Returns:
            Dictionary mapping symbol to signal
        """
        if len(data) < self.long_window:
            return {self.symbol: 'HOLD'}
        
        # Calculate moving averages
        short_ma = data['close'].rolling(window=self.short_window).mean()
        long_ma = data['close'].rolling(window=self.long_window).mean()
        
        # Get current and previous values
        current_short = short_ma.iloc[-1]
        current_long = long_ma.iloc[-1]
        
        if len(data) < self.long_window + 1:
            return {self.symbol: 'HOLD'}
        
        prev_short = short_ma.iloc[-2]
        prev_long = long_ma.iloc[-2]
        
        # Check for crossover
        if (prev_short <= prev_long and current_short > current_long):
            # Golden cross - buy signal
            return {self.symbol: 'BUY'}
        elif (prev_short >= prev_long and current_short < current_long):
            # Death cross - sell signal
            return {self.symbol: 'SELL'}
        else:
            return {self.symbol: 'HOLD'}
    
    def get_parameters(self) -> Dict[str, any]:
        """Get strategy parameters."""
        return {
            'short_window': self.short_window,
            'long_window': self.long_window,
            'symbol': self.symbol
        }
    
    def set_parameters(self, **kwargs):
        """Set strategy parameters."""
        if 'short_window' in kwargs:
            self.short_window = kwargs['short_window']
        if 'long_window' in kwargs:
            self.long_window = kwargs['long_window']
        if 'symbol' in kwargs:
            self.symbol = kwargs['symbol']
        
        # Validate parameters
        if self.short_window >= self.long_window:
            raise ValueError("Short window must be less than long window")
