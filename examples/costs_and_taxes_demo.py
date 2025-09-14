"""
Demo script showing trading costs and tax functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_fetcher import DataFetcher
from src.strategies.moving_average import MovingAverageStrategy
from src.backtesting.engine import BacktestEngine
from config.settings import get_setting
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_costs_and_taxes_demo():
    """Run a comprehensive demo of trading costs and tax functionality."""
    print("="*80)
    print("TRADING COSTS AND TAXES DEMO")
    print("="*80)
    
    # Fetch data
    print("\n1. Fetching historical data...")
    fetcher = DataFetcher()
    
    try:
        data = fetcher.get_data(
            symbol='AAPL',
            start='2022-01-01',
            end='2023-01-01'
        )
        print(f"✓ Fetched {len(data)} records for AAPL")
        print(f"  Date range: {data.index[0].date()} to {data.index[-1].date()}")
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        return
    
    # Test different cost and tax configurations
    configurations = [
        {
            'name': 'No Costs, No Taxes',
            'trading_costs': {
                'cost_type': 'fixed',
                'fixed_cost_per_trade': 0.0,
                'percentage_cost_per_trade': 0.0,
                'apply_to_buy': True,
                'apply_to_sell': True,
                'currency': 'EUR'
            },
            'tax_config': {
                'tax_rate': 0.0,
                'apply_immediately': True,
                'tax_on_realized_gains_only': True,
                'tax_free_threshold': 0.0,
                'currency': 'EUR'
            }
        },
        {
            'name': 'Fixed Costs (10 EUR per trade), No Taxes',
            'trading_costs': {
                'cost_type': 'fixed',
                'fixed_cost_per_trade': 10.0,
                'percentage_cost_per_trade': 0.0,
                'apply_to_buy': True,
                'apply_to_sell': True,
                'currency': 'EUR'
            },
            'tax_config': {
                'tax_rate': 0.0,
                'apply_immediately': True,
                'tax_on_realized_gains_only': True,
                'tax_free_threshold': 0.0,
                'currency': 'EUR'
            }
        },
        {
            'name': 'Percentage Costs (0.2%), No Taxes',
            'trading_costs': {
                'cost_type': 'percentage',
                'fixed_cost_per_trade': 0.0,
                'percentage_cost_per_trade': 0.002,  # 0.2%
                'apply_to_buy': True,
                'apply_to_sell': True,
                'currency': 'EUR'
            },
            'tax_config': {
                'tax_rate': 0.0,
                'apply_immediately': True,
                'tax_on_realized_gains_only': True,
                'tax_free_threshold': 0.0,
                'currency': 'EUR'
            }
        },
        {
            'name': 'Fixed Costs + 25% Tax on Profits',
            'trading_costs': {
                'cost_type': 'fixed',
                'fixed_cost_per_trade': 10.0,
                'percentage_cost_per_trade': 0.0,
                'apply_to_buy': True,
                'apply_to_sell': True,
                'currency': 'EUR'
            },
            'tax_config': {
                'tax_rate': 0.25,  # 25%
                'apply_immediately': True,
                'tax_on_realized_gains_only': True,
                'tax_free_threshold': 0.0,
                'currency': 'EUR'
            }
        },
        {
            'name': 'Percentage Costs + 25% Tax on Profits',
            'trading_costs': {
                'cost_type': 'percentage',
                'fixed_cost_per_trade': 0.0,
                'percentage_cost_per_trade': 0.002,  # 0.2%
                'apply_to_buy': True,
                'apply_to_sell': True,
                'currency': 'EUR'
            },
            'tax_config': {
                'tax_rate': 0.25,  # 25%
                'apply_immediately': True,
                'tax_on_realized_gains_only': True,
                'tax_free_threshold': 0.0,
                'currency': 'EUR'
            }
        },
        {
            'name': 'High Costs + High Taxes (Realistic)',
            'trading_costs': {
                'cost_type': 'percentage',
                'fixed_cost_per_trade': 0.0,
                'percentage_cost_per_trade': 0.005,  # 0.5%
                'apply_to_buy': True,
                'apply_to_sell': True,
                'currency': 'EUR'
            },
            'tax_config': {
                'tax_rate': 0.30,  # 30%
                'apply_immediately': True,
                'tax_on_realized_gains_only': True,
                'tax_free_threshold': 0.0,
                'currency': 'EUR'
            }
        }
    ]
    
    results = {}
    
    print(f"\n2. Testing {len(configurations)} different cost/tax configurations...")
    print("-" * 60)
    
    for config in configurations:
        print(f"\nTesting: {config['name']}")
        print("-" * 40)
        
        # Create strategy
        strategy = MovingAverageStrategy(
            short_window=20,
            long_window=50,
            symbol='AAPL'
        )
        
        # Create engine with custom configuration
        engine = BacktestEngine(
            initial_capital=10000,
            commission=0.001,  # Keep legacy commission for backward compatibility
            trading_costs_config=config['trading_costs'],
            tax_config=config['tax_config']
        )
        
        try:
            result = engine.run_backtest(data, strategy)
            results[config['name']] = result
            
            # Print summary
            summary = result.summary()
            print(f"  Final Value: ${summary['final_value']:.2f}")
            print(f"  Total Return: {summary['total_return']}")
            print(f"  Total Trades: {summary['total_trades']}")
            print(f"  Commission Paid: {summary['commission_paid']}")
            print(f"  Trading Costs Paid: {summary['trading_costs_paid']}")
            print(f"  Taxes Paid: {summary['taxes_paid']}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Compare results
    print(f"\n3. COMPARISON OF RESULTS")
    print("="*80)
    
    comparison_data = []
    for name, result in results.items():
        summary = result.summary()
        comparison_data.append({
            'Configuration': name,
            'Final Value': f"${summary['final_value']:.2f}",
            'Total Return': summary['total_return'],
            'Total Trades': summary['total_trades'],
            'Commission': summary['commission_paid'],
            'Trading Costs': summary['trading_costs_paid'],
            'Taxes': summary['taxes_paid']
        })
    
    # Print comparison table
    print(f"{'Configuration':<35} {'Final Value':<12} {'Return':<10} {'Trades':<8} {'Commission':<12} {'Trading Costs':<15} {'Taxes':<10}")
    print("-" * 120)
    
    for row in comparison_data:
        print(f"{row['Configuration']:<35} {row['Final Value']:<12} {row['Total Return']:<10} {row['Total Trades']:<8} {row['Commission']:<12} {row['Trading Costs']:<15} {row['Taxes']:<10}")
    
    # Show detailed trade analysis for one configuration
    if results:
        print(f"\n4. DETAILED TRADE ANALYSIS")
        print("-" * 60)
        
        # Use the configuration with both costs and taxes
        detailed_config = "Fixed Costs + 25% Tax on Profits"
        if detailed_config in results:
            result = results[detailed_config]
            trades_df = result.get_trades_dataframe()
            
            if not trades_df.empty:
                print(f"\nTrade Details for: {detailed_config}")
                print(f"Total Trades: {len(trades_df)}")
                
                # Show first few trades
                print(f"\nFirst 5 trades:")
                print(trades_df.head().to_string(index=False))
                
                # Show last few trades
                print(f"\nLast 5 trades:")
                print(trades_df.tail().to_string(index=False))
                
                # Calculate total costs and taxes
                total_commission = trades_df['commission'].sum()
                total_trading_costs = trades_df['trading_cost'].sum()
                total_taxes = trades_df['tax_paid'].sum() if 'tax_paid' in trades_df.columns else 0
                
                print(f"\nCost Breakdown:")
                print(f"  Total Commission: ${total_commission:.2f}")
                print(f"  Total Trading Costs: ${total_trading_costs:.2f}")
                print(f"  Total Taxes: ${total_taxes:.2f}")
                print(f"  Total Costs: ${total_commission + total_trading_costs + total_taxes:.2f}")
                
                # Show profit/loss analysis
                if 'profit' in trades_df.columns:
                    profitable_trades = trades_df[trades_df['profit'] > 0]
                    losing_trades = trades_df[trades_df['profit'] < 0]
                    
                    print(f"\nProfit/Loss Analysis:")
                    print(f"  Profitable Trades: {len(profitable_trades)}")
                    print(f"  Losing Trades: {len(losing_trades)}")
                    if len(profitable_trades) > 0:
                        print(f"  Average Profit: ${profitable_trades['profit'].mean():.2f}")
                    if len(losing_trades) > 0:
                        print(f"  Average Loss: ${losing_trades['profit'].mean():.2f}")
    
    print(f"\n5. KEY INSIGHTS")
    print("-" * 60)
    
    if len(results) >= 2:
        # Compare first (no costs) vs last (high costs)
        no_costs = list(results.values())[0]
        high_costs = list(results.values())[-1]
        
        no_costs_return = no_costs.metrics['total_return']
        high_costs_return = high_costs.metrics['total_return']
        
        print(f"• Impact of costs and taxes on returns:")
        print(f"  - No costs/taxes: {no_costs_return:.2%}")
        print(f"  - High costs/taxes: {high_costs_return:.2%}")
        print(f"  - Difference: {(high_costs_return - no_costs_return):.2%}")
        
        print(f"\n• Cost structure matters:")
        print(f"  - Fixed costs: Predictable, affects small trades more")
        print(f"  - Percentage costs: Scales with trade size")
        print(f"  - Taxes: Only on profits, reduces net gains")
    
    print(f"\n" + "="*80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nNext steps:")
    print("1. Experiment with different cost structures")
    print("2. Test different tax rates and thresholds")
    print("3. Analyze impact on different strategies")
    print("4. Consider realistic cost structures for your market")


if __name__ == "__main__":
    run_costs_and_taxes_demo()
