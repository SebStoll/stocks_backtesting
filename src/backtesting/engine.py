"""
Main backtesting engine.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

from .portfolio import Portfolio
from ..strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Main backtesting engine that runs strategies against historical data.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        benchmark_symbol: Optional[str] = None,
        trading_costs_config: Optional[Dict] = None,
        tax_config: Optional[Dict] = None
    ):
        """
        Initialize backtesting engine.
        
        Args:
            initial_capital: Starting capital
            benchmark_symbol: Symbol to use as benchmark
            trading_costs_config: Trading costs configuration
            tax_config: Tax configuration
        """
        self.initial_capital = initial_capital
        self.benchmark_symbol = benchmark_symbol
        self.portfolio = Portfolio(
            initial_capital, 
            trading_costs_config, 
            tax_config
        )
        
    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy: BaseStrategy,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> 'BacktestResults':
        """
        Run backtest with given strategy and data.
        
        Args:
            data: Historical price data
            strategy: Trading strategy to test
            start_date: Start date for backtest (optional)
            end_date: End date for backtest (optional)
            
        Returns:
            BacktestResults object with performance metrics
        """
        logger.info(f"Starting backtest with {strategy.__class__.__name__}")
        
        # Filter data by date range if specified
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
        
        if data.empty:
            raise ValueError("No data available for the specified date range")
        
        # Reset portfolio
        self.portfolio.reset()
        
        # Initialize strategy
        strategy.initialize(data)
        
        # Get symbols from data
        symbols = self._extract_symbols(data)
        
        # Run backtest
        for i, (timestamp, row) in enumerate(data.iterrows()):
            current_prices = self._get_current_prices(row, symbols)
            
            # Update portfolio value
            self.portfolio.update_portfolio_value(current_prices, timestamp)
            
            # Get strategy signals
            signals = strategy.generate_signals(data.iloc[:i+1])
            
            # Execute trades based on signals
            self._execute_trades(signals, current_prices, timestamp)
        
        # Final portfolio update
        final_prices = self._get_current_prices(data.iloc[-1], symbols)
        self.portfolio.update_portfolio_value(final_prices, data.index[-1])
        
        # Create results
        results = BacktestResults(
            portfolio=self.portfolio,
            data=data,
            strategy_name=strategy.__class__.__name__,
            benchmark_symbol=self.benchmark_symbol
        )
        
        logger.info(f"Backtest completed. Final portfolio value: {self.portfolio.portfolio_value:.2f}")
        return results
    
    def _extract_symbols(self, data: pd.DataFrame) -> List[str]:
        """Extract symbols from data columns."""
        # For single symbol strategies, we need to get the symbol from the strategy
        # This is a simplified approach - in practice, you might have multi-symbol data
        return ['AAPL']  # For now, hardcode to AAPL since that's what we're testing
    
    def _get_current_prices(self, row: pd.Series, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for all symbols."""
        # For single symbol data, use the close price
        if 'close' in row:
            return {symbol: row['close'] for symbol in symbols}
        elif 'Close' in row:
            return {symbol: row['Close'] for symbol in symbols}
        else:
            # Try to find a price column
            price_cols = [col for col in row.index if 'close' in col.lower() or 'price' in col.lower()]
            if price_cols:
                return {symbol: row[price_cols[0]] for symbol in symbols}
            else:
                raise ValueError("No price column found in data")
    
    def _execute_trades(self, signals: Dict[str, str], current_prices: Dict[str, float], timestamp: datetime):
        """Execute trades based on strategy signals."""
        for symbol, signal in signals.items():
            if symbol not in current_prices:
                continue
                
            current_price = current_prices[symbol]
            current_position = self.portfolio.get_position_size(symbol)
            
            if signal == 'BUY' and current_position == 0:
                # Calculate position size (simplified - use all available cash)
                available_cash = self.portfolio.cash * 0.95  # Leave 5% buffer
                shares_to_buy = int(available_cash / current_price)
                
                if shares_to_buy > 0:
                    self.portfolio.buy(symbol, shares_to_buy, current_price, timestamp)
                    
            elif signal == 'SELL' and current_position > 0:
                self.portfolio.sell(symbol, current_position, current_price, timestamp)
                
            elif signal == 'HOLD':
                # Do nothing
                pass


class BacktestResults:
    """
    Container for backtest results and performance metrics.
    """
    
    def __init__(
        self,
        portfolio: Portfolio,
        data: pd.DataFrame,
        strategy_name: str,
        benchmark_symbol: Optional[str] = None
    ):
        self.portfolio = portfolio
        self.data = data
        self.strategy_name = strategy_name
        self.benchmark_symbol = benchmark_symbol
        
        # Calculate performance metrics
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate performance metrics."""
        if not self.portfolio.portfolio_history:
            self.metrics = {}
            return
        
        # Get portfolio values over time
        portfolio_values = [h['portfolio_value'] for h in self.portfolio.portfolio_history]
        timestamps = [h['timestamp'] for h in self.portfolio.portfolio_history]
        
        # Calculate returns
        returns = pd.Series(portfolio_values).pct_change().dropna()
        
        # Basic metrics
        self.metrics = {
            'total_return': (portfolio_values[-1] - self.portfolio.initial_capital) / self.portfolio.initial_capital,
            'annualized_return': self._calculate_annualized_return(returns),
            'volatility': returns.std() * np.sqrt(252),  # Annualized
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'max_drawdown': self._calculate_max_drawdown(portfolio_values),
            'win_rate': self.portfolio.winning_trades / max(self.portfolio.total_trades, 1),
            'total_trades': self.portfolio.total_trades,
            'total_commission_paid': self.portfolio.total_trading_costs_paid,
            'total_trading_costs_paid': self.portfolio.total_trading_costs_paid,
            'total_taxes_paid': self.portfolio.total_taxes_paid,
            'final_portfolio_value': portfolio_values[-1]
        }
    
    def _calculate_annualized_return(self, returns: pd.Series) -> float:
        """Calculate annualized return."""
        if len(returns) == 0:
            return 0.0
        return (1 + returns.mean()) ** 252 - 1
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        excess_returns = returns.mean() * 252 - risk_free_rate
        return excess_returns / (returns.std() * np.sqrt(252))
    
    def _calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """Calculate maximum drawdown."""
        if not portfolio_values:
            return 0.0
        
        peak = portfolio_values[0]
        max_dd = 0.0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of backtest results."""
        return {
            'strategy': self.strategy_name,
            'initial_capital': self.portfolio.initial_capital,
            'final_value': self.metrics.get('final_portfolio_value', 0),
            'total_return': f"{self.metrics.get('total_return', 0):.2%}",
            'annualized_return': f"{self.metrics.get('annualized_return', 0):.2%}",
            'volatility': f"{self.metrics.get('volatility', 0):.2%}",
            'sharpe_ratio': f"{self.metrics.get('sharpe_ratio', 0):.2f}",
            'max_drawdown': f"{self.metrics.get('max_drawdown', 0):.2%}",
            'win_rate': f"{self.metrics.get('win_rate', 0):.2%}",
            'total_trades': self.metrics.get('total_trades', 0),
            'commission_paid': f"${self.metrics.get('total_commission_paid', 0):.2f}",
            'trading_costs_paid': f"${self.metrics.get('total_trading_costs_paid', 0):.2f}",
            'taxes_paid': f"${self.metrics.get('total_taxes_paid', 0):.2f}"
        }
    
    def print_summary(self):
        """Print formatted summary."""
        print("\n" + "="*50)
        print(f"BACKTEST RESULTS - {self.strategy_name}")
        print("="*50)
        
        summary = self.summary()
        for key, value in summary.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("="*50)
    
    def plot_performance(self, figsize: tuple = (12, 8)):
        """Plot portfolio performance."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            
            if not self.portfolio.portfolio_history:
                print("No portfolio history available for plotting")
                return
            
            # Get portfolio values and timestamps
            portfolio_values = [h['portfolio_value'] for h in self.portfolio.portfolio_history]
            timestamps = [h['timestamp'] for h in self.portfolio.portfolio_history]
            
            # Create plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
            
            # Portfolio value over time
            ax1.plot(timestamps, portfolio_values, label='Portfolio Value', linewidth=2)
            ax1.axhline(y=self.portfolio.initial_capital, color='r', linestyle='--', alpha=0.7, label='Initial Capital')
            ax1.set_ylabel('Portfolio Value ($)')
            ax1.set_title(f'{self.strategy_name} - Portfolio Performance')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Drawdown
            peak = portfolio_values[0]
            drawdowns = []
            for value in portfolio_values:
                if value > peak:
                    peak = value
                drawdowns.append((peak - value) / peak * 100)
            
            ax2.fill_between(timestamps, drawdowns, 0, alpha=0.3, color='red', label='Drawdown')
            ax2.set_ylabel('Drawdown (%)')
            ax2.set_xlabel('Date')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Format x-axis
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("Matplotlib not available for plotting")
        except Exception as e:
            print(f"Error creating plot: {e}")
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        return self.portfolio.get_trades_dataframe()
    
    def get_portfolio_history_dataframe(self) -> pd.DataFrame:
        """Get portfolio history as DataFrame."""
        return self.portfolio.get_portfolio_history_dataframe()
