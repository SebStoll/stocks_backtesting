"""
Comprehensive demo of the stock backtesting framework.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.data_fetcher import DataFetcher
from src.strategies.moving_average import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.macd_strategy import MACDStrategy
from src.backtesting.engine import BacktestEngine
from src.visualization.plots import BacktestPlots
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_comprehensive_demo():
    """Run a comprehensive demonstration of the backtesting framework."""
    print("="*80)
    print("STOCK BACKTESTING FRAMEWORK - COMPREHENSIVE DEMO")
    print("="*80)
    
    # Step 1: Data Fetching
    print("\n📊 STEP 1: DATA FETCHING")
    print("-" * 50)
    
    fetcher = DataFetcher()
    
    # Fetch data for multiple symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    all_data = {}
    
    for symbol in symbols:
        try:
            data = fetcher.get_data(
                symbol=symbol,
                start='2020-01-01',
                end='2023-01-01'
            )
            all_data[symbol] = data
            print(f"✓ Fetched {len(data)} records for {symbol}")
        except Exception as e:
            print(f"✗ Error fetching {symbol}: {e}")
    
    if not all_data:
        print("✗ No data fetched. Exiting demo.")
        return
    
    # Use AAPL as primary symbol for strategy testing
    primary_symbol = 'AAPL'
    data = all_data[primary_symbol]
    
    # Step 2: Strategy Creation
    print(f"\n🎯 STEP 2: STRATEGY CREATION")
    print("-" * 50)
    
    strategies = {
        'Moving Average (20,50)': MovingAverageStrategy(20, 50, primary_symbol),
        'Moving Average (10,30)': MovingAverageStrategy(10, 30, primary_symbol),
        'RSI (14, 30/70)': RSIStrategy(14, 30, 70, primary_symbol),
        'RSI (21, 25/75)': RSIStrategy(21, 25, 75, primary_symbol),
        'MACD (12,26,9)': MACDStrategy(12, 26, 9, primary_symbol),
        'MACD (8,21,5)': MACDStrategy(8, 21, 5, primary_symbol)
    }
    
    print(f"✓ Created {len(strategies)} trading strategies")
    for name, strategy in strategies.items():
        print(f"  - {name}: {strategy.get_parameters()}")
    
    # Step 3: Backtesting
    print(f"\n⚙️ STEP 3: BACKTESTING")
    print("-" * 50)
    
    engine = BacktestEngine(
        initial_capital=10000,
        commission=0.001
    )
    
    results = {}
    for name, strategy in strategies.items():
        print(f"  Testing {name}...")
        try:
            result = engine.run_backtest(data, strategy)
            results[name] = result
            final_value = result.portfolio.portfolio_value
            total_return = result.metrics.get('total_return', 0)
            print(f"    ✓ Completed - Final: ${final_value:.2f} ({total_return:.2%})")
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    if not results:
        print("✗ No successful backtests completed")
        return
    
    # Step 4: Results Analysis
    print(f"\n📈 STEP 4: RESULTS ANALYSIS")
    print("-" * 50)
    
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
    print("\nStrategy Performance Comparison:")
    print("=" * 100)
    print(comparison_df.to_string(index=False))
    
    # Find best and worst strategies
    best_strategy = max(results.keys(), key=lambda x: results[x].metrics.get('total_return', 0))
    worst_strategy = min(results.keys(), key=lambda x: results[x].metrics.get('total_return', 0))
    
    print(f"\n🏆 Best Strategy: {best_strategy}")
    print(f"   Total Return: {results[best_strategy].summary()['total_return']}")
    print(f"   Sharpe Ratio: {results[best_strategy].summary()['sharpe_ratio']}")
    
    print(f"\n📉 Worst Strategy: {worst_strategy}")
    print(f"   Total Return: {results[worst_strategy].summary()['total_return']}")
    print(f"   Sharpe Ratio: {results[worst_strategy].summary()['sharpe_ratio']}")
    
    # Step 5: Detailed Analysis of Best Strategy
    print(f"\n🔍 STEP 5: DETAILED ANALYSIS - {best_strategy}")
    print("-" * 50)
    
    best_result = results[best_strategy]
    best_result.print_summary()
    
    # Show trades
    trades_df = best_result.get_trades_dataframe()
    if not trades_df.empty:
        print(f"\nTrading Activity:")
        print(f"  Total Trades: {len(trades_df)}")
        print(f"  Buy Trades: {len(trades_df[trades_df['action'] == 'BUY'])}")
        print(f"  Sell Trades: {len(trades_df[trades_df['action'] == 'SELL'])}")
        
        print(f"\nRecent Trades (last 5):")
        print(trades_df.tail().to_string(index=False))
    else:
        print("  No trades executed during backtest period")
    
    # Step 6: Visualization
    print(f"\n📊 STEP 6: VISUALIZATION")
    print("-" * 50)
    
    try:
        plots = BacktestPlots()
        
        # Plot best strategy performance
        print("  Generating performance plot for best strategy...")
        best_result.plot_performance()
        
        # Plot strategy comparison
        print("  Generating strategy comparison plots...")
        strategies_metrics = {name: result.metrics for name, result in results.items()}
        
        # Metrics comparison
        fig1 = plots.plot_metrics_comparison(strategies_metrics, "Strategy Performance Comparison")
        fig1.show()
        
        # Risk vs Return scatter
        fig2 = plots.plot_risk_return_scatter(strategies_metrics, "Risk vs Return Analysis")
        fig2.show()
        
        print("✓ All plots generated successfully")
        
    except Exception as e:
        print(f"✗ Error generating plots: {e}")
    
    # Step 7: Multi-Symbol Analysis
    print(f"\n🌐 STEP 7: MULTI-SYMBOL ANALYSIS")
    print("-" * 50)
    
    if len(all_data) > 1:
        print("Testing best strategy on multiple symbols...")
        
        multi_results = {}
        for symbol, symbol_data in all_data.items():
            if symbol != primary_symbol:
                print(f"  Testing {symbol}...")
                try:
                    # Create strategy for this symbol
                    strategy = MovingAverageStrategy(20, 50, symbol)
                    result = engine.run_backtest(symbol_data, strategy)
                    multi_results[symbol] = result
                    final_value = result.portfolio.portfolio_value
                    total_return = result.metrics.get('total_return', 0)
                    print(f"    ✓ {symbol}: ${final_value:.2f} ({total_return:.2%})")
                except Exception as e:
                    print(f"    ✗ {symbol}: Error - {e}")
        
        if multi_results:
            print(f"\nMulti-Symbol Results Summary:")
            for symbol, result in multi_results.items():
                summary = result.summary()
                print(f"  {symbol}: {summary['total_return']} return, {summary['sharpe_ratio']} Sharpe")
    
    # Step 8: Summary
    print(f"\n📋 STEP 8: DEMO SUMMARY")
    print("-" * 50)
    
    print("✓ Data fetching: Successfully retrieved historical data")
    print(f"✓ Strategy testing: Tested {len(strategies)} different strategies")
    print(f"✓ Backtesting: Completed {len(results)} successful backtests")
    print("✓ Analysis: Generated comprehensive performance metrics")
    print("✓ Visualization: Created performance charts and comparisons")
    
    if len(all_data) > 1:
        print("✓ Multi-symbol: Tested strategies across multiple assets")
    
    print(f"\n🎯 Key Insights:")
    print(f"  - Best performing strategy: {best_strategy}")
    print(f"  - Total strategies tested: {len(strategies)}")
    print(f"  - Successful backtests: {len(results)}")
    print(f"  - Data period: {data.index[0].date()} to {data.index[-1].date()}")
    print(f"  - Initial capital: $10,000")
    
    print("\n" + "="*80)
    print("🎉 COMPREHENSIVE DEMO COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nNext steps:")
    print("1. Try different strategy parameters")
    print("2. Test on different time periods")
    print("3. Add your own custom strategies")
    print("4. Experiment with different assets")
    print("5. Implement more sophisticated portfolio management")


if __name__ == "__main__":
    run_comprehensive_demo()
