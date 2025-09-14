"""
Simple example of running a backtest with moving average strategy.
Fixed version with better error handling.
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from src.data.data_fetcher import DataFetcher
    from src.strategies.moving_average import MovingAverageStrategy
    from src.backtesting.engine import BacktestEngine
    import logging
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please make sure you're running this from the project root directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Run a simple backtest example."""
    print("="*60)
    print("STOCK BACKTESTING FRAMEWORK - SIMPLE EXAMPLE")
    print("="*60)
    
    # Fetch data
    print("\n1. Fetching historical data...")
    try:
        fetcher = DataFetcher()
        data = fetcher.get_data(
            symbol='AAPL',
            start='2020-01-01',
            end='2023-01-01'
        )
        print(f"✓ Fetched {len(data)} records for AAPL")
        print(f"  Date range: {data.index[0].date()} to {data.index[-1].date()}")
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        print("This might be due to network issues or yfinance not being installed")
        return
    
    # Create strategy
    print("\n2. Creating trading strategy...")
    try:
        strategy = MovingAverageStrategy(
            short_window=20,
            long_window=50,
            symbol='AAPL'
        )
        print(f"✓ Created strategy: {strategy}")
    except Exception as e:
        print(f"✗ Error creating strategy: {e}")
        return
    
    # Run backtest
    print("\n3. Running backtest...")
    try:
        engine = BacktestEngine(
            initial_capital=10000,
            commission=0.001
        )
        results = engine.run_backtest(data, strategy)
        print("✓ Backtest completed successfully")
    except Exception as e:
        print(f"✗ Error running backtest: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n4. Backtest Results:")
    print("-" * 40)
    try:
        results.print_summary()
    except Exception as e:
        print(f"✗ Error displaying results: {e}")
        return
    
    # Show some trades
    try:
        trades_df = results.get_trades_dataframe()
        if not trades_df.empty:
            print(f"\n5. Recent Trades (showing last 5):")
            print("-" * 40)
            print(trades_df.tail().to_string(index=False))
        else:
            print("\n5. No trades executed during backtest period")
    except Exception as e:
        print(f"✗ Error displaying trades: {e}")
    
    # Plot results
    print("\n6. Generating performance plot...")
    try:
        results.plot_performance()
        print("✓ Performance plot generated")
    except Exception as e:
        print(f"✗ Error generating plot: {e}")
        print("This might be due to matplotlib not being properly configured")
    
    print("\n" + "="*60)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("="*60)


if __name__ == "__main__":
    main()
