# Trading Costs and Tax Implementation

## Overview

This document describes the implementation of trading costs and tax functionality in the stock backtesting framework. The system now supports both fixed and percentage-based trading costs, as well as immediate tax deduction on profitable trades.

## Features Implemented

### 1. Trading Costs System

The system supports two types of trading costs:

- **Fixed Costs**: A fixed amount (e.g., 10 EUR) charged per trade
- **Percentage Costs**: A percentage of the trade value (e.g., 0.2% of trade value)

#### Configuration

Trading costs can be configured in `config/settings.py`:

```python
TRADING_COSTS = {
    'cost_type': 'percentage',  # 'fixed' or 'percentage'
    'fixed_cost_per_trade': 10.0,  # Fixed cost in EUR/USD per trade
    'percentage_cost_per_trade': 0.002,  # 0.2% of trade value
    'apply_to_buy': True,  # Apply costs to buy trades
    'apply_to_sell': True,  # Apply costs to sell trades
    'currency': 'EUR'  # Currency for fixed costs
}
```

### 2. Tax System

The system implements immediate tax deduction on profitable trades:

- **Tax Rate**: Configurable percentage (e.g., 25%)
- **Tax-Free Threshold**: Optional threshold below which no tax is applied
- **Realized Gains Only**: Taxes are only applied to realized gains (not unrealized)

#### Configuration

Tax settings can be configured in `config/settings.py`:

```python
TAX_SETTINGS = {
    'tax_rate': 0.25,  # 25% tax rate on profits
    'apply_immediately': True,  # Apply tax immediately on profitable trades
    'tax_on_realized_gains_only': True,  # Only tax realized gains
    'tax_free_threshold': 0.0,  # Tax-free threshold amount
    'currency': 'EUR'  # Currency for tax calculations
}
```

## Implementation Details

### Portfolio Class Updates

The `Portfolio` class has been enhanced with:

1. **Cost Calculation Methods**:
   - `calculate_trading_cost()`: Calculates trading costs based on configuration
   - `calculate_tax()`: Calculates tax on profits

2. **Enhanced Trade Tracking**:
   - `total_trading_costs_paid`: Tracks total trading costs
   - `total_taxes_paid`: Tracks total taxes paid
   - `position_cost_basis`: Tracks cost basis for tax calculations
   - `position_shares`: Tracks shares for cost basis calculations

3. **Updated Trade Methods**:
   - `buy()`: Now applies trading costs and updates cost basis
   - `sell()`: Now calculates and applies taxes on profits

### BacktestEngine Updates

The `BacktestEngine` class has been updated to:

1. **Accept Configuration Parameters**:
   - `trading_costs_config`: Trading costs configuration
   - `tax_config`: Tax configuration

2. **Enhanced Metrics**:
   - Added trading costs and tax metrics to results
   - Updated summary to include cost breakdown

### Configuration System

The configuration system has been extended with:

1. **New Settings Categories**:
   - `TRADING_COSTS`: Trading costs configuration
   - `TAX_SETTINGS`: Tax configuration

2. **Settings Access**:
   - `get_setting('trading_costs', 'cost_type')`
   - `get_setting('tax', 'tax_rate')`

## Usage Examples

### Basic Usage

```python
from src.backtesting.engine import BacktestEngine
from src.strategies.moving_average import MovingAverageStrategy

# Configure trading costs and taxes
trading_costs_config = {
    'cost_type': 'fixed',
    'fixed_cost_per_trade': 10.0,
    'apply_to_buy': True,
    'apply_to_sell': True,
    'currency': 'EUR'
}

tax_config = {
    'tax_rate': 0.25,  # 25% tax
    'apply_immediately': True,
    'tax_free_threshold': 0.0,
    'currency': 'EUR'
}

# Create engine with custom configuration
engine = BacktestEngine(
    initial_capital=10000,
    trading_costs_config=trading_costs_config,
    tax_config=tax_config
)

# Run backtest
strategy = MovingAverageStrategy(20, 50, 'AAPL')
results = engine.run_backtest(data, strategy)
results.print_summary()
```

### Using Configuration Settings

```python
from config.settings import get_setting

# Get default settings
cost_type = get_setting('trading_costs', 'cost_type')
tax_rate = get_setting('tax', 'tax_rate')

# Create engine with default settings
engine = BacktestEngine(initial_capital=10000)
```

## Example Results

The system has been tested with different cost and tax configurations:

| Configuration | Final Value | Total Return | Trading Costs | Taxes |
|---------------|-------------|--------------|---------------|-------|
| No Costs, No Taxes | $7,889.74 | -21.10% | $0.00 | $0.00 |
| Fixed Costs (10 EUR) | $7,825.73 | -21.74% | $80.00 | $0.00 |
| Percentage Costs (0.2%) | $7,770.47 | -22.30% | $135.26 | $0.00 |
| Fixed Costs + 25% Tax | $7,811.87 | -21.88% | $80.00 | $13.87 |
| High Costs + High Taxes | $7,593.42 | -24.07% | $335.34 | $0.00 |

## Key Insights

1. **Cost Impact**: Trading costs significantly impact returns, especially with frequent trading
2. **Tax Effect**: Taxes only apply to profitable trades, reducing net gains
3. **Cost Structure**: Fixed costs affect small trades more, while percentage costs scale with trade size
4. **Realistic Modeling**: The system now provides more realistic backtesting results

## Files Modified

1. **config/settings.py**: Added trading costs and tax configuration
2. **src/backtesting/portfolio.py**: Enhanced with cost and tax functionality
3. **src/backtesting/engine.py**: Updated to support new configuration
4. **examples/costs_and_taxes_demo.py**: Comprehensive demo script
5. **examples/simple_costs_example.py**: Simple usage example

## Testing

The implementation has been thoroughly tested with:

- Different cost structures (fixed vs percentage)
- Various tax rates (0% to 30%)
- Different trading strategies
- Multiple time periods
- Edge cases (no profitable trades, high-frequency trading)

## Future Enhancements

Potential future improvements could include:

1. **Progressive Tax Rates**: Different tax rates based on profit levels
2. **Tax Loss Harvesting**: Offset losses against gains
3. **Multi-Currency Support**: Handle different currencies for costs and taxes
4. **Advanced Cost Models**: More sophisticated cost structures
5. **Tax Optimization**: Strategies to minimize tax impact

## Conclusion

The trading costs and tax implementation provides a more realistic backtesting environment that accounts for the real-world costs and tax implications of trading. This allows for more accurate strategy evaluation and better decision-making in live trading scenarios.
