"""
Performance metrics calculation for backtesting results.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Calculate comprehensive performance metrics for backtesting results.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize performance metrics calculator.
        
        Args:
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_all_metrics(
        self,
        portfolio_values: List[float],
        returns: pd.Series,
        trades: pd.DataFrame,
        initial_capital: float
    ) -> Dict[str, float]:
        """
        Calculate all performance metrics.
        
        Args:
            portfolio_values: Portfolio values over time
            returns: Portfolio returns
            trades: Trades DataFrame
            initial_capital: Initial capital
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}
        
        # Basic return metrics
        metrics.update(self._calculate_return_metrics(portfolio_values, initial_capital))
        
        # Risk metrics
        metrics.update(self._calculate_risk_metrics(returns))
        
        # Trade metrics
        metrics.update(self._calculate_trade_metrics(trades))
        
        # Advanced metrics
        metrics.update(self._calculate_advanced_metrics(returns, portfolio_values))
        
        return metrics
    
    def _calculate_return_metrics(
        self,
        portfolio_values: List[float],
        initial_capital: float
    ) -> Dict[str, float]:
        """Calculate return-related metrics."""
        if not portfolio_values:
            return {}
        
        final_value = portfolio_values[-1]
        total_return = (final_value - initial_capital) / initial_capital
        
        # Calculate annualized return
        if len(portfolio_values) > 1:
            # Assume daily data
            days = len(portfolio_values)
            years = days / 252
            annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        else:
            annualized_return = 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'final_value': final_value,
            'initial_capital': initial_capital
        }
    
    def _calculate_risk_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate risk-related metrics."""
        if returns.empty:
            return {}
        
        # Volatility (annualized)
        volatility = returns.std() * np.sqrt(252)
        
        # Sharpe ratio
        if volatility > 0:
            excess_return = returns.mean() * 252 - self.risk_free_rate
            sharpe_ratio = excess_return / volatility
        else:
            sharpe_ratio = 0
        
        # Maximum drawdown
        max_drawdown = self._calculate_max_drawdown(returns)
        
        # Value at Risk (VaR) - 95% confidence
        var_95 = np.percentile(returns, 5)
        
        # Conditional Value at Risk (CVaR)
        cvar_95 = returns[returns <= var_95].mean()
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'cvar_95': cvar_95
        }
    
    def _calculate_trade_metrics(self, trades: pd.DataFrame) -> Dict[str, float]:
        """Calculate trade-related metrics."""
        if trades.empty:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        # Count trades by type
        buy_trades = trades[trades['action'] == 'BUY']
        sell_trades = trades[trades['action'] == 'SELL']
        
        total_trades = len(trades)
        
        # Calculate P&L for each completed trade
        trade_pnl = []
        for symbol in trades['symbol'].unique():
            symbol_trades = trades[trades['symbol'] == symbol].sort_values('timestamp')
            
            buy_cost = 0
            sell_proceeds = 0
            
            for _, trade in symbol_trades.iterrows():
                if trade['action'] == 'BUY':
                    buy_cost += trade['cost']
                elif trade['action'] == 'SELL':
                    sell_proceeds += trade['proceeds']
            
            if buy_cost > 0 and sell_proceeds > 0:
                pnl = sell_proceeds - buy_cost
                trade_pnl.append(pnl)
        
        if not trade_pnl:
            return {
                'total_trades': total_trades,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        # Calculate trade statistics
        winning_trades = [pnl for pnl in trade_pnl if pnl > 0]
        losing_trades = [pnl for pnl in trade_pnl if pnl < 0]
        
        win_rate = len(winning_trades) / len(trade_pnl) if trade_pnl else 0
        
        # Profit factor
        total_wins = sum(winning_trades) if winning_trades else 0
        total_losses = abs(sum(losing_trades)) if losing_trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Average win/loss
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        
        # Largest win/loss
        largest_win = max(winning_trades) if winning_trades else 0
        largest_loss = min(losing_trades) if losing_trades else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss
        }
    
    def _calculate_advanced_metrics(
        self,
        returns: pd.Series,
        portfolio_values: List[float]
    ) -> Dict[str, float]:
        """Calculate advanced performance metrics."""
        if returns.empty:
            return {}
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        
        if downside_deviation > 0:
            excess_return = returns.mean() * 252 - self.risk_free_rate
            sortino_ratio = excess_return / downside_deviation
        else:
            sortino_ratio = 0
        
        # Calmar ratio (annual return / max drawdown)
        annual_return = returns.mean() * 252
        max_drawdown = self._calculate_max_drawdown(returns)
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        # Information ratio (if benchmark available)
        # This would require benchmark returns
        information_ratio = 0  # Placeholder
        
        # Skewness and Kurtosis
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        # Recovery factor
        recovery_factor = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        return {
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'information_ratio': information_ratio,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'recovery_factor': recovery_factor
        }
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        if returns.empty:
            return 0.0
        
        # Calculate cumulative returns
        cumulative_returns = (1 + returns).cumprod()
        
        # Calculate running maximum
        running_max = cumulative_returns.expanding().max()
        
        # Calculate drawdown
        drawdown = (cumulative_returns - running_max) / running_max
        
        return abs(drawdown.min())
    
    def calculate_rolling_metrics(
        self,
        returns: pd.Series,
        window: int = 252
    ) -> pd.DataFrame:
        """
        Calculate rolling performance metrics.
        
        Args:
            returns: Portfolio returns
            window: Rolling window size
            
        Returns:
            DataFrame with rolling metrics
        """
        if returns.empty:
            return pd.DataFrame()
        
        rolling_data = {}
        
        # Rolling returns
        rolling_data['rolling_return'] = returns.rolling(window).mean() * 252
        
        # Rolling volatility
        rolling_data['rolling_volatility'] = returns.rolling(window).std() * np.sqrt(252)
        
        # Rolling Sharpe ratio
        rolling_data['rolling_sharpe'] = (
            rolling_data['rolling_return'] - self.risk_free_rate
        ) / rolling_data['rolling_volatility']
        
        # Rolling maximum drawdown
        rolling_data['rolling_max_dd'] = returns.rolling(window).apply(
            lambda x: self._calculate_max_drawdown(x)
        )
        
        return pd.DataFrame(rolling_data)
    
    def compare_with_benchmark(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> Dict[str, float]:
        """
        Compare strategy performance with benchmark.
        
        Args:
            strategy_returns: Strategy returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Dictionary of comparison metrics
        """
        if strategy_returns.empty or benchmark_returns.empty:
            return {}
        
        # Align the series
        aligned_data = pd.DataFrame({
            'strategy': strategy_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if aligned_data.empty:
            return {}
        
        strategy_ret = aligned_data['strategy']
        benchmark_ret = aligned_data['benchmark']
        
        # Excess returns
        excess_returns = strategy_ret - benchmark_ret
        
        # Tracking error
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        # Information ratio
        information_ratio = excess_returns.mean() * 252 / tracking_error if tracking_error > 0 else 0
        
        # Beta
        covariance = np.cov(strategy_ret, benchmark_ret)[0, 1]
        benchmark_variance = np.var(benchmark_ret)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
        
        # Alpha
        alpha = (strategy_ret.mean() - self.risk_free_rate) - beta * (benchmark_ret.mean() - self.risk_free_rate)
        alpha *= 252  # Annualize
        
        # Correlation
        correlation = strategy_ret.corr(benchmark_ret)
        
        return {
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'beta': beta,
            'alpha': alpha,
            'correlation': correlation
        }
