"""
Unit tests for trading strategies.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.moving_average import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.macd_strategy import MACDStrategy


class TestMovingAverageStrategy(unittest.TestCase):
    """Test MovingAverageStrategy class."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample price data
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        self.data = pd.DataFrame({
            'open': prices,
            'high': prices + np.random.rand(100) * 2,
            'low': prices - np.random.rand(100) * 2,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        self.strategy = MovingAverageStrategy(short_window=5, long_window=10)
    
    def test_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.short_window, 5)
        self.assertEqual(self.strategy.long_window, 10)
        self.assertEqual(self.strategy.symbol, 'SYMBOL')
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        with self.assertRaises(ValueError):
            MovingAverageStrategy(short_window=10, long_window=5)
    
    def test_generate_signals_insufficient_data(self):
        """Test signal generation with insufficient data."""
        short_data = self.data.iloc[:5]
        signals = self.strategy.generate_signals(short_data)
        self.assertEqual(signals['SYMBOL'], 'HOLD')
    
    def test_generate_signals_sufficient_data(self):
        """Test signal generation with sufficient data."""
        signals = self.strategy.generate_signals(self.data)
        self.assertIn(signals['SYMBOL'], ['BUY', 'SELL', 'HOLD'])
    
    def test_get_parameters(self):
        """Test parameter retrieval."""
        params = self.strategy.get_parameters()
        self.assertEqual(params['short_window'], 5)
        self.assertEqual(params['long_window'], 10)
        self.assertEqual(params['symbol'], 'SYMBOL')


class TestRSIStrategy(unittest.TestCase):
    """Test RSIStrategy class."""
    
    def setUp(self):
        """Set up test data."""
        dates = pd.date_range('2020-01-01', periods=50, freq='D')
        prices = 100 + np.cumsum(np.random.randn(50) * 0.5)
        
        self.data = pd.DataFrame({
            'open': prices,
            'high': prices + np.random.rand(50) * 2,
            'low': prices - np.random.rand(50) * 2,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 50)
        }, index=dates)
        
        self.strategy = RSIStrategy(period=14, oversold_threshold=30, overbought_threshold=70)
    
    def test_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.period, 14)
        self.assertEqual(self.strategy.oversold_threshold, 30)
        self.assertEqual(self.strategy.overbought_threshold, 70)
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        with self.assertRaises(ValueError):
            RSIStrategy(oversold_threshold=70, overbought_threshold=30)
        
        with self.assertRaises(ValueError):
            RSIStrategy(oversold_threshold=-10)
        
        with self.assertRaises(ValueError):
            RSIStrategy(overbought_threshold=110)
    
    def test_calculate_rsi(self):
        """Test RSI calculation."""
        # Create trending data
        trending_data = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
        rsi = self.strategy.calculate_rsi(trending_data)
        
        # RSI should be high for trending up data
        self.assertGreater(rsi.iloc[-1], 50)
    
    def test_generate_signals(self):
        """Test signal generation."""
        signals = self.strategy.generate_signals(self.data)
        self.assertIn(signals['SYMBOL'], ['BUY', 'SELL', 'HOLD'])


class TestMACDStrategy(unittest.TestCase):
    """Test MACDStrategy class."""
    
    def setUp(self):
        """Set up test data."""
        dates = pd.date_range('2020-01-01', periods=50, freq='D')
        prices = 100 + np.cumsum(np.random.randn(50) * 0.5)
        
        self.data = pd.DataFrame({
            'open': prices,
            'high': prices + np.random.rand(50) * 2,
            'low': prices - np.random.rand(50) * 2,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 50)
        }, index=dates)
        
        self.strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
    
    def test_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.fast_period, 12)
        self.assertEqual(self.strategy.slow_period, 26)
        self.assertEqual(self.strategy.signal_period, 9)
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        with self.assertRaises(ValueError):
            MACDStrategy(fast_period=26, slow_period=12)
    
    def test_calculate_macd(self):
        """Test MACD calculation."""
        macd_line, signal_line, histogram = self.strategy.calculate_macd(self.data['close'])
        
        # Check that all series have the same length
        self.assertEqual(len(macd_line), len(self.data))
        self.assertEqual(len(signal_line), len(self.data))
        self.assertEqual(len(histogram), len(self.data))
    
    def test_generate_signals(self):
        """Test signal generation."""
        signals = self.strategy.generate_signals(self.data)
        self.assertIn(signals['SYMBOL'], ['BUY', 'SELL', 'HOLD'])


if __name__ == '__main__':
    unittest.main()
