"""
Simple example showing how to configure trading costs and taxes.
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
    """Run a simple example with trading costs and taxes."""
    print("="*60)
    print("SIMPLE TRADING COSTS AND TAXES EXAMPLE")
    print("="*60)
    
    # Fetch data
    print("\n1. Fetching data...")
    fetcher = DataFetcher()
    data = fetcher.get_data(symbol='AAPL', start='2022-01-01', end='2023-01-01')
    print(f"✓ Fetched {len(data)} records")
    
    # Create strategy
    print("\n2. Creating strategy...")
    strategy = MovingAverageStrategy(short_window=20, long_window=50, symbol='AAPL')
    
    # Example 1: Fixed costs (10 EUR per trade) + 25% tax
    print("\n3. Example 1: Fixed costs + taxes")
    print("-" * 40)
    
    trading_costs_config = {
        'cost_type': 'fixed',
        'fixed_cost_per_trade': 10.0,  # 10 EUR per trade
        'percentage_cost_per_trade': 0.0,
        'apply_to_buy': True,
        'apply_to_sell': True,
        'currency': 'EUR'
    }
    
    tax_config = {
        'tax_rate': 0.25,  # 25% tax on profits
        'apply_immediately': True,
        'tax_on_realized_gains_only': True,
        'tax_free_threshold': 0.0,
        'currency': 'EUR'
    }
    
    engine1 = BacktestEngine(
        initial_capital=10000,
        trading_costs_config=trading_costs_config,
        tax_config=tax_config
    )
    
    result1 = engine1.run_backtest(data, strategy)
    result1.print_summary()
    
    # Example 2: Percentage costs (0.2%) + 30% tax
    print("\n4. Example 2: Percentage costs + higher taxes")
    print("-" * 40)
    
    trading_costs_config2 = {
        'cost_type': 'percentage',
        'fixed_cost_per_trade': 0.0,
        'percentage_cost_per_trade': 0.002,  # 0.2% of trade value
        'apply_to_buy': True,
        'apply_to_sell': True,
        'currency': 'EUR'
    }
    
    tax_config2 = {
        'tax_rate': 0.30,  # 30% tax on profits
        'apply_immediately': True,
        'tax_on_realized_gains_only': True,
        'tax_free_threshold': 0.0,
        'currency': 'EUR'
    }
    
    engine2 = BacktestEngine(
        initial_capital=10000,
        trading_costs_config=trading_costs_config2,
        tax_config=tax_config2
    )
    
    result2 = engine2.run_backtest(data, strategy)
    result2.print_summary()
    
    # Show some trades
    print("\n5. Sample trades from Example 1:")
    print("-" * 40)
    trades_df = result1.get_trades_dataframe()
    if not trades_df.empty:
        print(trades_df.head(10).to_string(index=False))
    
    print("\n" + "="*60)
    print("EXAMPLE COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    main()
