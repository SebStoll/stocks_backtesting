"""
Demo script showing the flexible data source functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_fetcher import DataFetcher
from src.data.data_source_factory import DataSourceFactory
from config.settings import get_setting
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demonstrate_data_source_flexibility():
    """Demonstrate the flexible data source architecture."""
    print("="*80)
    print("FLEXIBLE DATA SOURCE ARCHITECTURE DEMO")
    print("="*80)
    
    # 1. Show available data sources
    print("\n1. AVAILABLE DATA SOURCES")
    print("-" * 50)
    available_sources = DataSourceFactory.get_available_sources()
    print(f"Available data sources: {available_sources}")
    
    # 2. Create DataFetcher with default source
    print("\n2. CREATING DATAFETCHER WITH DEFAULT SOURCE")
    print("-" * 50)
    fetcher = DataFetcher()
    print(f"Current data source: {fetcher.get_current_data_source()}")
    print(f"Default source from config: {get_setting('data', 'default_data_source')}")
    
    # 3. Show configuration
    print("\n3. DATA SOURCE CONFIGURATION")
    print("-" * 50)
    yahoo_config = get_setting('data_source', 'yahoo_finance', {})
    print(f"Yahoo Finance configuration: {yahoo_config}")
    
    # 4. Demonstrate data fetching (if network is available)
    print("\n4. DATA FETCHING DEMONSTRATION")
    print("-" * 50)
    try:
        # Try to fetch a small amount of data
        data = fetcher.get_data(
            symbol='AAPL',
            start='2023-12-01',
            end='2023-12-05'
        )
        print(f"✓ Successfully fetched {len(data)} records for AAPL")
        print(f"  Date range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"  Columns: {list(data.columns)}")
        print(f"  Sample data:")
        print(data.head(2))
    except Exception as e:
        print(f"✗ Error fetching data (this is expected if offline): {e}")
        print("  This demonstrates error handling in the data source abstraction")
    
    # 5. Show how to switch data sources (conceptual)
    print("\n5. SWITCHING DATA SOURCES")
    print("-" * 50)
    print("To switch to a different data source, you can:")
    print("1. Use the switch_data_source method:")
    print("   fetcher.switch_data_source('new_source_name', param1='value1')")
    print("2. Create a new DataFetcher with specific source:")
    print("   fetcher = DataFetcher(data_source='new_source_name')")
    print("3. Update configuration in settings.py")
    
    # 6. Show how to add new data sources
    print("\n6. ADDING NEW DATA SOURCES")
    print("-" * 50)
    print("To add a new data source:")
    print("1. Create a class inheriting from BaseDataSource")
    print("2. Implement required methods: get_data, get_info, get_dividends")
    print("3. Register with DataSourceFactory:")
    print("   DataSourceFactory.register_source('my_source', MyDataSource)")
    print("4. Add configuration to settings.py")
    
    # 7. Show data validation
    print("\n7. DATA VALIDATION")
    print("-" * 50)
    print("The data source abstraction includes built-in validation:")
    print("- Required columns: open, high, low, close, volume")
    print("- DatetimeIndex requirement")
    print("- Data normalization (column name standardization)")
    print("- Empty data detection")
    
    print("\n" + "="*80)
    print("DEMO COMPLETED - DATA SOURCE ARCHITECTURE IS READY!")
    print("="*80)


if __name__ == "__main__":
    demonstrate_data_source_flexibility()
