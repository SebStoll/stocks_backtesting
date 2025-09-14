"""
Unit tests for data source abstraction.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.base_data_source import BaseDataSource
from src.data.yahoo_finance_source import YahooFinanceDataSource
from src.data.data_source_factory import DataSourceFactory
from src.data.data_fetcher import DataFetcher


class MockDataSource(BaseDataSource):
    """Mock data source for testing."""
    
    def get_data(self, symbol, start, end=None, interval='1d', **kwargs):
        """Mock get_data implementation."""
        # Create mock data
        dates = pd.date_range(start='2020-01-01', end='2020-01-10', freq='D')
        data = pd.DataFrame({
            'open': np.random.randn(len(dates)) * 100 + 100,
            'high': np.random.randn(len(dates)) * 100 + 105,
            'low': np.random.randn(len(dates)) * 100 + 95,
            'close': np.random.randn(len(dates)) * 100 + 100,
            'volume': np.random.randint(1000, 10000, len(dates))
        }, index=dates)
        
        return self.normalize_data(data)
    
    def get_info(self, symbol: str) -> Dict[str, Any]:
        """Mock get_info implementation."""
        return {
            'symbol': symbol,
            'name': f'Test Company {symbol}',
            'sector': 'Technology',
            'marketCap': 1000000000
        }
    
    def get_dividends(self, symbol: str, start=None, end=None) -> pd.DataFrame:
        """Mock get_dividends implementation."""
        dates = pd.date_range(start='2020-01-01', end='2020-01-10', freq='Q')
        dividends = pd.Series(
            [0.5, 0.6, 0.7, 0.8],
            index=dates[:4]
        )
        return dividends


class TestBaseDataSource(unittest.TestCase):
    """Test cases for BaseDataSource."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_source = MockDataSource()
    
    def test_initialization(self):
        """Test data source initialization."""
        config = {'test_param': 'test_value'}
        source = MockDataSource(**config)
        self.assertEqual(source.config['test_param'], 'test_value')
        self.assertIsInstance(source.cache, dict)
    
    def test_validate_data_valid(self):
        """Test data validation with valid data."""
        dates = pd.date_range(start='2020-01-01', end='2020-01-10', freq='D')
        data = pd.DataFrame({
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100] * 10,
            'volume': [1000] * 10
        }, index=dates)
        
        self.assertTrue(self.data_source.validate_data(data))
    
    def test_validate_data_missing_columns(self):
        """Test data validation with missing columns."""
        dates = pd.date_range(start='2020-01-01', end='2020-01-10', freq='D')
        data = pd.DataFrame({
            'open': [100] * 10,
            'high': [105] * 10,
            # Missing low, close, volume
        }, index=dates)
        
        self.assertFalse(self.data_source.validate_data(data))
    
    def test_validate_data_empty(self):
        """Test data validation with empty data."""
        data = pd.DataFrame()
        self.assertFalse(self.data_source.validate_data(data))
    
    def test_validate_data_wrong_index(self):
        """Test data validation with wrong index type."""
        data = pd.DataFrame({
            'open': [100],
            'high': [105],
            'low': [95],
            'close': [100],
            'volume': [1000]
        }, index=[0])  # Not a DatetimeIndex
        
        self.assertFalse(self.data_source.validate_data(data))
    
    def test_normalize_data(self):
        """Test data normalization."""
        dates = pd.date_range(start='2020-01-01', end='2020-01-10', freq='D')
        data = pd.DataFrame({
            'Open': [100] * 10,  # Capital O
            'High': [105] * 10,
            'Low': [95] * 10,
            'Close': [100] * 10,
            'Volume': [1000] * 10
        }, index=dates)
        
        normalized = self.data_source.normalize_data(data)
        
        # Check column names are normalized
        expected_columns = ['open', 'high', 'low', 'close', 'volume']
        self.assertEqual(list(normalized.columns), expected_columns)
        
        # Check data is sorted by date
        self.assertTrue(normalized.index.is_monotonic_increasing)
    
    def test_get_cache_key(self):
        """Test cache key generation."""
        key = self.data_source.get_cache_key(
            'AAPL', '2020-01-01', '2020-01-10', '1d', param1='value1'
        )
        
        self.assertIsInstance(key, str)
        self.assertIn('AAPL', key)
        self.assertIn('2020-01-01', key)
        self.assertIn('2020-01-10', key)
        self.assertIn('1d', key)
    
    def test_clear_cache(self):
        """Test cache clearing."""
        self.data_source.cache['test_key'] = 'test_value'
        self.data_source.clear_cache()
        self.assertEqual(len(self.data_source.cache), 0)


class TestYahooFinanceDataSource(unittest.TestCase):
    """Test cases for YahooFinanceDataSource."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_source = YahooFinanceDataSource()
    
    def test_initialization(self):
        """Test Yahoo Finance data source initialization."""
        config = {'timeout': 15, 'max_retries': 5}
        source = YahooFinanceDataSource(**config)
        self.assertEqual(source.timeout, 15)
        self.assertEqual(source.max_retries, 5)
    
    def test_initialization_defaults(self):
        """Test default configuration values."""
        self.assertEqual(self.data_source.timeout, 10)
        self.assertEqual(self.data_source.max_retries, 3)
        self.assertEqual(self.data_source.retry_delay, 1.0)
    
    def test_validate_config_invalid_timeout(self):
        """Test configuration validation with invalid timeout."""
        with self.assertRaises(ValueError):
            YahooFinanceDataSource(timeout=-1)
    
    def test_validate_config_invalid_retries(self):
        """Test configuration validation with invalid retries."""
        with self.assertRaises(ValueError):
            YahooFinanceDataSource(max_retries=-1)
    
    def test_validate_config_invalid_delay(self):
        """Test configuration validation with invalid delay."""
        with self.assertRaises(ValueError):
            YahooFinanceDataSource(retry_delay=-1)
    
    @patch('yfinance.Ticker')
    def test_get_data_success(self, mock_ticker):
        """Test successful data fetching."""
        # Mock yfinance response
        mock_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [100, 101, 102],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2020-01-01', periods=3))
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        result = self.data_source.get_data('AAPL', '2020-01-01', '2020-01-03')
        
        # Verify yfinance was called correctly
        mock_ticker.assert_called_once_with('AAPL')
        mock_ticker_instance.history.assert_called_once()
        
        # Verify result format
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertIn('open', result.columns)
        self.assertIn('high', result.columns)
        self.assertIn('low', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
    
    @patch('yfinance.Ticker')
    def test_get_data_empty_response(self, mock_ticker):
        """Test data fetching with empty response."""
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance
        
        with self.assertRaises(ValueError):
            self.data_source.get_data('INVALID', '2020-01-01', '2020-01-03')
    
    @patch('yfinance.Ticker')
    def test_get_info_success(self, mock_ticker):
        """Test successful info fetching."""
        mock_info = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_info
        mock_ticker.return_value = mock_ticker_instance
        
        result = self.data_source.get_info('AAPL')
        
        self.assertEqual(result, mock_info)
        mock_ticker.assert_called_once_with('AAPL')
    
    @patch('yfinance.Ticker')
    def test_get_dividends_success(self, mock_ticker):
        """Test successful dividend fetching."""
        mock_dividends = pd.Series(
            [0.5, 0.6],
            index=pd.date_range('2020-01-01', periods=2, freq='Q')
        )
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.dividends = mock_dividends
        mock_ticker.return_value = mock_ticker_instance
        
        result = self.data_source.get_dividends('AAPL')
        
        pd.testing.assert_series_equal(result, mock_dividends)
        mock_ticker.assert_called_once_with('AAPL')


class TestDataSourceFactory(unittest.TestCase):
    """Test cases for DataSourceFactory."""
    
    def test_get_available_sources(self):
        """Test getting available data sources."""
        sources = DataSourceFactory.get_available_sources()
        self.assertIn('yahoo_finance', sources)
        self.assertIsInstance(sources, list)
    
    def test_create_source_success(self):
        """Test successful source creation."""
        source = DataSourceFactory.create_source('yahoo_finance', timeout=15)
        self.assertIsInstance(source, YahooFinanceDataSource)
        self.assertEqual(source.timeout, 15)
    
    def test_create_source_invalid(self):
        """Test source creation with invalid name."""
        with self.assertRaises(ValueError):
            DataSourceFactory.create_source('invalid_source')
    
    def test_register_source(self):
        """Test registering a new data source."""
        # Register mock source
        DataSourceFactory.register_source('mock', MockDataSource)
        
        # Verify it's available
        self.assertIn('mock', DataSourceFactory.get_available_sources())
        
        # Test creating it
        source = DataSourceFactory.create_source('mock')
        self.assertIsInstance(source, MockDataSource)
    
    def test_register_invalid_source(self):
        """Test registering invalid source class."""
        with self.assertRaises(ValueError):
            DataSourceFactory.register_source('invalid', str)  # str doesn't inherit from BaseDataSource
    
    def test_is_source_available(self):
        """Test checking source availability."""
        self.assertTrue(DataSourceFactory.is_source_available('yahoo_finance'))
        self.assertFalse(DataSourceFactory.is_source_available('nonexistent'))


class TestDataFetcher(unittest.TestCase):
    """Test cases for DataFetcher."""
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_initialization_default_source(self, mock_factory):
        """Test DataFetcher initialization with default source."""
        mock_source = Mock()
        mock_factory.create_source.return_value = mock_source
        
        fetcher = DataFetcher()
        
        mock_factory.create_source.assert_called_once()
        self.assertEqual(fetcher.data_source, mock_source)
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_initialization_custom_source(self, mock_factory):
        """Test DataFetcher initialization with custom source."""
        mock_source = Mock()
        mock_factory.create_source.return_value = mock_source
        
        fetcher = DataFetcher(data_source='custom_source', custom_param='value')
        
        mock_factory.create_source.assert_called_once_with('custom_source', custom_param='value')
        self.assertEqual(fetcher.data_source, mock_source)
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_get_data_delegation(self, mock_factory):
        """Test that get_data delegates to data source."""
        mock_source = Mock()
        mock_data = pd.DataFrame({'test': [1, 2, 3]})
        mock_source.get_data.return_value = mock_data
        mock_factory.create_source.return_value = mock_source
        
        fetcher = DataFetcher()
        result = fetcher.get_data('AAPL', '2020-01-01', '2020-01-10')
        
        mock_source.get_data.assert_called_once_with('AAPL', '2020-01-01', '2020-01-10', '1d')
        pd.testing.assert_frame_equal(result, mock_data)
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_get_info_delegation(self, mock_factory):
        """Test that get_info delegates to data source."""
        mock_source = Mock()
        mock_info = {'symbol': 'AAPL', 'name': 'Apple Inc.'}
        mock_source.get_info.return_value = mock_info
        mock_factory.create_source.return_value = mock_source
        
        fetcher = DataFetcher()
        result = fetcher.get_info('AAPL')
        
        mock_source.get_info.assert_called_once_with('AAPL')
        self.assertEqual(result, mock_info)
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_get_dividends_delegation(self, mock_factory):
        """Test that get_dividends delegates to data source."""
        mock_source = Mock()
        mock_dividends = pd.Series([0.5, 0.6])
        mock_source.get_dividends.return_value = mock_dividends
        mock_factory.create_source.return_value = mock_source
        
        fetcher = DataFetcher()
        result = fetcher.get_dividends('AAPL', '2020-01-01', '2020-01-10')
        
        mock_source.get_dividends.assert_called_once_with('AAPL', '2020-01-01', '2020-01-10')
        pd.testing.assert_series_equal(result, mock_dividends)
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_switch_data_source(self, mock_factory):
        """Test switching data source."""
        mock_source1 = Mock()
        mock_source2 = Mock()
        mock_factory.create_source.side_effect = [mock_source1, mock_source2]
        
        fetcher = DataFetcher()
        self.assertEqual(fetcher.data_source, mock_source1)
        
        fetcher.switch_data_source('new_source', param='value')
        self.assertEqual(fetcher.data_source, mock_source2)
        mock_factory.create_source.assert_called_with('new_source', param='value')
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_get_current_data_source(self, mock_factory):
        """Test getting current data source name."""
        mock_source = Mock()
        mock_source.__class__.__name__ = 'YahooFinanceDataSource'
        mock_factory.create_source.return_value = mock_source
        
        fetcher = DataFetcher()
        result = fetcher.get_current_data_source()
        
        self.assertEqual(result, 'YahooFinanceDataSource')
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_get_available_data_sources(self, mock_factory):
        """Test getting available data sources."""
        mock_sources = ['yahoo_finance', 'alpha_vantage']
        mock_factory.get_available_sources.return_value = mock_sources
        mock_factory.create_source.return_value = Mock()
        
        fetcher = DataFetcher()
        result = fetcher.get_available_data_sources()
        
        self.assertEqual(result, mock_sources)
        mock_factory.get_available_sources.assert_called_once()
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_clear_cache_delegation(self, mock_factory):
        """Test that clear_cache delegates to data source."""
        mock_source = Mock()
        mock_factory.create_source.return_value = mock_source
        
        fetcher = DataFetcher()
        fetcher.clear_cache()
        
        mock_source.clear_cache.assert_called_once()
    
    @patch('src.data.data_fetcher.DataSourceFactory')
    def test_validate_data_delegation(self, mock_factory):
        """Test that validate_data delegates to data source."""
        mock_source = Mock()
        mock_source.validate_data.return_value = True
        mock_factory.create_source.return_value = mock_source
        
        test_data = pd.DataFrame({'test': [1, 2, 3]})
        fetcher = DataFetcher()
        result = fetcher.validate_data(test_data)
        
        mock_source.validate_data.assert_called_once_with(test_data)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
