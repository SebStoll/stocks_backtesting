# Data Source Architecture

This document describes the flexible data source architecture implemented in the stocks backtesting framework.

## Overview

The framework now uses a flexible, pluggable data source architecture that allows easy switching between different data providers and makes it simple to add new data sources in the future.

## Architecture Components

### 1. BaseDataSource (Abstract Interface)

**Location**: `src/data/base_data_source.py`

The `BaseDataSource` class defines the standard interface that all data sources must implement:

```python
class BaseDataSource(ABC):
    def get_data(symbol, start, end=None, interval='1d', **kwargs) -> pd.DataFrame
    def get_info(symbol) -> Dict[str, Any]
    def get_dividends(symbol, start=None, end=None) -> pd.DataFrame
```

**Key Features**:
- Standardized data format (OHLCV columns: open, high, low, close, volume)
- Built-in data validation
- Data normalization (column name standardization)
- Caching support
- Error handling

### 2. YahooFinanceDataSource (Concrete Implementation)

**Location**: `src/data/yahoo_finance_source.py`

The current implementation using Yahoo Finance as the data source.

**Configuration**:
```python
{
    'timeout': 10,        # Request timeout in seconds
    'max_retries': 3,     # Maximum number of retries
    'retry_delay': 1.0    # Delay between retries in seconds
}
```

### 3. DataSourceFactory (Factory Pattern)

**Location**: `src/data/data_source_factory.py`

Manages data source creation and registration:

```python
# Get available sources
sources = DataSourceFactory.get_available_sources()

# Create a data source
source = DataSourceFactory.create_source('yahoo_finance', timeout=15)

# Register a new data source
DataSourceFactory.register_source('my_source', MyDataSource)
```

### 4. DataFetcher (Facade)

**Location**: `src/data/data_fetcher.py`

The main interface used by the rest of the application:

```python
# Create with default source
fetcher = DataFetcher()

# Create with specific source
fetcher = DataFetcher(data_source='yahoo_finance', timeout=15)

# Switch data source at runtime
fetcher.switch_data_source('new_source', param='value')
```

## Configuration

Data source configuration is managed in `config/settings.py`:

```python
# Default data source
DATA_SETTINGS = {
    'default_data_source': 'yahoo_finance'
}

# Data source specific settings
DATA_SOURCE_SETTINGS = {
    'yahoo_finance': {
        'timeout': 10,
        'max_retries': 3,
        'retry_delay': 1.0
    }
}
```

## Usage Examples

### Basic Usage

```python
from src.data.data_fetcher import DataFetcher

# Create fetcher with default source
fetcher = DataFetcher()

# Fetch data
data = fetcher.get_data('AAPL', '2020-01-01', '2023-01-01')

# Get company info
info = fetcher.get_info('AAPL')

# Get dividends
dividends = fetcher.get_dividends('AAPL', '2020-01-01', '2023-01-01')
```

### Switching Data Sources

```python
# Switch to a different source
fetcher.switch_data_source('alpha_vantage', api_key='your_key')

# Or create a new fetcher with specific source
fetcher = DataFetcher(data_source='alpha_vantage', api_key='your_key')
```

### Adding New Data Sources

1. **Create a new data source class**:

```python
from src.data.base_data_source import BaseDataSource

class MyDataSource(BaseDataSource):
    def get_data(self, symbol, start, end=None, interval='1d', **kwargs):
        # Implement data fetching logic
        pass
    
    def get_info(self, symbol):
        # Implement info fetching logic
        pass
    
    def get_dividends(self, symbol, start=None, end=None):
        # Implement dividend fetching logic
        pass
```

2. **Register the data source**:

```python
from src.data.data_source_factory import DataSourceFactory

DataSourceFactory.register_source('my_source', MyDataSource)
```

3. **Add configuration**:

```python
# In config/settings.py
DATA_SOURCE_SETTINGS = {
    'my_source': {
        'api_key': 'your_api_key',
        'timeout': 30
    }
}
```

## Data Format Standardization

All data sources must return data in the following standardized format:

### OHLCV Data
- **Index**: DatetimeIndex
- **Columns**: 
  - `open`: Opening price
  - `high`: High price
  - `low`: Low price
  - `close`: Closing price
  - `volume`: Trading volume
- **Additional columns**: May include `dividends`, `stock_splits`, etc.

### Company Info
- **Type**: Dictionary
- **Content**: Company metadata (name, sector, market cap, etc.)

### Dividends
- **Type**: pandas.Series
- **Index**: DatetimeIndex
- **Values**: Dividend amounts

## Error Handling

The architecture includes comprehensive error handling:

- **Data validation**: Ensures required columns and proper format
- **Network errors**: Handles connection timeouts and retries
- **Data source errors**: Provides meaningful error messages
- **Configuration errors**: Validates data source configuration

## Testing

Comprehensive unit tests are provided in `tests/test_data_sources.py`:

- BaseDataSource functionality
- YahooFinanceDataSource implementation
- DataSourceFactory operations
- DataFetcher facade
- Error handling scenarios

Run tests with:
```bash
python -m unittest tests.test_data_sources -v
```

## Migration from Old Architecture

The new architecture is backward compatible. Existing code using `DataFetcher` will continue to work without changes:

```python
# Old code (still works)
from src.data.data_fetcher import DataFetcher
fetcher = DataFetcher()
data = fetcher.get_data('AAPL', '2020-01-01', '2023-01-01')
```

## Benefits

1. **Flexibility**: Easy to switch between data sources
2. **Extensibility**: Simple to add new data sources
3. **Maintainability**: Clear separation of concerns
4. **Testability**: Each component can be tested independently
5. **Configuration**: Centralized configuration management
6. **Error Handling**: Robust error handling and validation
7. **Backward Compatibility**: Existing code continues to work

## Future Data Sources

The architecture is designed to easily accommodate additional data sources:

- **Alpha Vantage**: Professional financial data API
- **IEX Cloud**: Real-time and historical market data
- **Polygon**: High-quality financial data
- **Quandl**: Economic and financial datasets
- **Custom APIs**: Any REST API that provides financial data

Each new data source only needs to implement the `BaseDataSource` interface and register with the `DataSourceFactory`.
