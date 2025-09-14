# Stock Backtesting Framework

A comprehensive Python framework for backtesting stock trading strategies against historical data.

## Features

- **Data Fetching**: Get historical stock data from Yahoo Finance
- **Strategy Framework**: Easy-to-use interface for implementing trading strategies
- **Backtesting Engine**: Robust portfolio management and trade execution
- **Performance Metrics**: Comprehensive analysis including returns, Sharpe ratio, drawdowns
- **Visualization**: Interactive charts and performance graphs
- **Example Strategies**: Moving average crossover, RSI, MACD, and more

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the example:
```bash
python examples/simple_strategy.py
```

## Project Structure

```
stocks_backtesting/
├── src/
│   ├── data/           # Data fetching and management
│   ├── strategies/     # Trading strategy implementations
│   ├── backtesting/    # Core backtesting engine
│   ├── metrics/        # Performance metrics calculation
│   └── visualization/  # Charts and graphs
├── examples/           # Example strategies and usage
├── tests/             # Unit tests
└── config/            # Configuration files
```

## Example Usage

```python
from src.data.data_fetcher import DataFetcher
from src.strategies.moving_average import MovingAverageStrategy
from src.backtesting.engine import BacktestEngine

# Fetch data
fetcher = DataFetcher()
data = fetcher.get_data('AAPL', start='2020-01-01', end='2023-01-01')

# Create strategy
strategy = MovingAverageStrategy(short_window=20, long_window=50)

# Run backtest
engine = BacktestEngine(initial_capital=10000)
results = engine.run_backtest(data, strategy)

# View results
print(results.summary())
results.plot_performance()
```

## Available Strategies

- Moving Average Crossover
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Mean Reversion
- Momentum
- Custom strategies (easy to implement)

## Performance Metrics

- Total Return
- Annualized Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor
- And many more...
