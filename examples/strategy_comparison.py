"""
Compare multiple trading strategies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_fetcher import DataFetcher
from src.strategies.moving_average import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.macd_strategy import MACDStrategy
from src.backtesting.engine import BacktestEngine
from src.visualization.plots import BacktestPlots
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Compare multiple trading strategies."""
    print("="*60)
    print("STOCK BACKTESTING FRAMEWORK - STRATEGY COMPARISON")
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
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        return
    
    # Define strategies to test
    strategies = {
        'Moving Average (20,50)': MovingAverageStrategy(20, 50, 'AAPL'),
        'Moving Average (10,30)': MovingAverageStrategy(10, 30, 'AAPL'),
        'RSI (14, 30/70)': RSIStrategy(14, 30, 70, 'AAPL'),
        'RSI (21, 25/75)': RSIStrategy(21, 25, 75, 'AAPL'),
        'MACD (12,26,9)': MACDStrategy(12, 26, 9, 'AAPL'),
        'MACD (8,21,5)': MACDStrategy(8, 21, 5, 'AAPL')
    }
    
    print(f"\n2. Testing {len(strategies)} strategies...")
    
    # Run backtests
    results = {}
    engine = BacktestEngine(initial_capital=10000, commission=0.001)
    
    for name, strategy in strategies.items():
        print(f"  Testing {name}...")
        try:
            result = engine.run_backtest(data, strategy)
            results[name] = result
            print(f"    ✓ Completed - Final value: ${result.portfolio.portfolio_value:.2f}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    if not results:
        print("✗ No successful backtests completed")
        return
    
    # Compare results
    print(f"\n3. Strategy Comparison Results:")
    print("="*80)
    
    # Create comparison table
    comparison_data = []
    for name, result in results.items():
        summary = result.summary()
        comparison_data.append({
            'Strategy': name,
            'Total Return': summary['total_return'],
            'Annualized Return': summary['annualized_return'],
            'Sharpe Ratio': summary['sharpe_ratio'],
            'Max Drawdown': summary['max_drawdown'],
            'Win Rate': summary['win_rate'],
            'Total Trades': summary['total_trades'],
            'Final Value': f"${summary['final_value']:.2f}"
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False))
    
    # Find best performing strategy
    best_strategy = max(results.keys(), key=lambda x: results[x].metrics.get('total_return', 0))
    print(f"\n4. Best Performing Strategy: {best_strategy}")
    print(f"   Total Return: {results[best_strategy].summary()['total_return']}")
    
    # Create comparison plots
    print("\n5. Generating comparison plots...")
    try:
        plots = BacktestPlots()
        
        # Extract metrics for plotting
        strategies_metrics = {}
        for name, result in results.items():
            strategies_metrics[name] = result.metrics
        
        # Plot comparison
        fig = plots.plot_metrics_comparison(strategies_metrics, "Strategy Performance Comparison")
        fig.show()
        
        # Plot risk vs return
        fig2 = plots.plot_risk_return_scatter(strategies_metrics, "Risk vs Return Analysis")
        fig2.show()
        
        print("✓ Comparison plots generated")
    except Exception as e:
        print(f"✗ Error generating plots: {e}")
    
    # Detailed analysis of best strategy
    print(f"\n6. Detailed Analysis - {best_strategy}:")
    print("-" * 50)
    results[best_strategy].print_summary()
    
    # Show trades for best strategy
    best_trades = results[best_strategy].get_trades_dataframe()
    if not best_trades.empty:
        print(f"\n7. Trades for {best_strategy}:")
        print("-" * 50)
        print(best_trades.to_string(index=False))
    
    print("\n" + "="*60)
    print("STRATEGY COMPARISON COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    main()
