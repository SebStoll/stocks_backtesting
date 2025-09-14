"""
Simple example of running a backtest with moving average strategy.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_fetcher import DataFetcher
from src.strategies.moving_average import MovingAverageStrategy
from src.backtesting.engine import BacktestEngine
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run a simple backtest example."""
    print("="*60)
    print("STOCK BACKTESTING FRAMEWORK - SIMPLE EXAMPLE")
    print("="*60)
    
    # Fetch data
    print("\n1. Fetching historical data...")
    fetcher = DataFetcher()
    
    try:
        data = fetcher.get_data(
            symbol='AAPL',
            start='2020-01-01',
            end='2023-01-01'
        )
        print(f"✓ Fetched {len(data)} records for AAPL")
        print(f"  Date range: {data.index[0].date()} to {data.index[-1].date()}")
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        return
    
    # Create strategy
    print("\n2. Creating trading strategy...")
    strategy = MovingAverageStrategy(
        short_window=20,
        long_window=50,
        symbol='AAPL'
    )
    print(f"✓ Created strategy: {strategy}")
    
    # Run backtest
    print("\n3. Running backtest...")
    engine = BacktestEngine(
        initial_capital=10000,
        commission=0.001
    )
    
    try:
        results = engine.run_backtest(data, strategy)
        print("✓ Backtest completed successfully")
    except Exception as e:
        print(f"✗ Error running backtest: {e}")
        return
    
    # Display results
    print("\n4. Backtest Results:")
    print("-" * 40)
    results.print_summary()
    
    # Show some trades
    trades_df = results.get_trades_dataframe()
    if not trades_df.empty:
        print(f"\n5. Recent Trades (showing last 5):")
        print("-" * 40)
        print(trades_df.tail().to_string(index=False))
    else:
        print("\n5. No trades executed during backtest period")
    
    # Plot results
    print("\n6. Generating performance plot...")
    try:
        results.plot_performance()
        print("✓ Performance plot generated")
    except Exception as e:
        print(f"✗ Error generating plot: {e}")
    
    print("\n" + "="*60)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("="*60)


if __name__ == "__main__":
    main()
