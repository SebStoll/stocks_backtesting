"""
Buy and Hold Strategy.

A simple benchmark strategy that buys at the beginning and holds until the end.
This strategy serves as a baseline for comparing other trading strategies.
"""

import pandas as pd
from typing import Dict, Optional
import logging

from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class BuyAndHoldStrategy(BaseStrategy):
    """
    Buy and Hold strategy.
    
    This strategy buys the stock at the beginning of the backtest period
    and holds it until the end. It serves as a benchmark for comparing
    other trading strategies.
    """
    
    def __init__(
        self,
        symbol: str = 'SYMBOL',
        name: Optional[str] = None
    ):
        """
        Initialize buy and hold strategy.
        
        Args:
            symbol: Symbol to trade
            name: Strategy name
        """
        super().__init__(name or "Buy and Hold")
        self.symbol = symbol
        self.bought = False
    
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        Generate trading signals for buy and hold strategy.
        
        Args:
            data: Historical data up to current point
            
        Returns:
            Dictionary mapping symbol to signal
        """
        # Buy at the very first opportunity
        if not self.bought and len(data) > 0:
            self.bought = True
            return {self.symbol: 'BUY'}
        
        # Hold for the rest of the time
        return {self.symbol: 'HOLD'}
    
    def get_parameters(self) -> Dict[str, any]:
        """Get strategy parameters."""
        return {
            'symbol': self.symbol
        }
    
    def set_parameters(self, **kwargs):
        """Set strategy parameters."""
        if 'symbol' in kwargs:
            self.symbol = kwargs['symbol']
    
    def reset(self):
        """Reset strategy state for new backtest."""
        self.bought = False
        self.initialized = False
        self.data = None
