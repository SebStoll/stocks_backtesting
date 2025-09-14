"""
Base strategy class for implementing trading strategies.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name (defaults to class name)
        """
        self.name = name or self.__class__.__name__
        self.initialized = False
        self.data = None
        
    def initialize(self, data: pd.DataFrame):
        """
        Initialize strategy with historical data.
        Called once before backtesting begins.
        
        Args:
            data: Historical price data
        """
        self.data = data
        self.initialized = True
        logger.info(f"Initialized strategy: {self.name}")
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        Generate trading signals based on current data.
        
        Args:
            data: Historical data up to current point
            
        Returns:
            Dictionary mapping symbol to signal ('BUY', 'SELL', 'HOLD')
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get strategy parameters.
        Override in subclasses to return parameter values.
        
        Returns:
            Dictionary of parameter names and values
        """
        return {}
    
    def set_parameters(self, **kwargs):
        """
        Set strategy parameters.
        Override in subclasses to handle parameter setting.
        
        Args:
            **kwargs: Parameter name-value pairs
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"Unknown parameter: {key}")
    
    
    def __str__(self):
        return f"{self.name}({self.get_parameters()})"
    
    def __repr__(self):
        return self.__str__()
