"""
Visualization functions for backtesting results.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class BacktestPlots:
    """
    Create various plots for backtesting results.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize plotting class.
        
        Args:
            figsize: Default figure size
        """
        self.figsize = figsize
    
    def plot_portfolio_performance(
        self,
        portfolio_values: List[float],
        timestamps: List,
        initial_capital: float,
        title: str = "Portfolio Performance",
        benchmark_values: Optional[List[float]] = None,
        benchmark_timestamps: Optional[List] = None,
        benchmark_label: str = "Benchmark"
    ) -> plt.Figure:
        """
        Plot portfolio value over time.
        
        Args:
            portfolio_values: Portfolio values over time
            timestamps: Timestamps for portfolio values
            initial_capital: Initial capital
            title: Plot title
            benchmark_values: Benchmark values (optional)
            benchmark_timestamps: Benchmark timestamps (optional)
            benchmark_label: Benchmark label
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot portfolio value
        ax.plot(timestamps, portfolio_values, label='Portfolio', linewidth=2, color='blue')
        
        # Plot initial capital line
        ax.axhline(y=initial_capital, color='red', linestyle='--', alpha=0.7, label='Initial Capital')
        
        # Plot benchmark if provided
        if benchmark_values and benchmark_timestamps:
            ax.plot(benchmark_timestamps, benchmark_values, label=benchmark_label, 
                   linewidth=2, color='green', alpha=0.7)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_drawdown(
        self,
        portfolio_values: List[float],
        timestamps: List,
        title: str = "Portfolio Drawdown"
    ) -> plt.Figure:
        """
        Plot portfolio drawdown over time.
        
        Args:
            portfolio_values: Portfolio values over time
            timestamps: Timestamps for portfolio values
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Calculate drawdown
        peak = portfolio_values[0]
        drawdowns = []
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            drawdowns.append(drawdown)
        
        # Plot drawdown
        ax.fill_between(timestamps, drawdowns, 0, alpha=0.3, color='red', label='Drawdown')
        ax.plot(timestamps, drawdowns, color='red', linewidth=1)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_returns_distribution(
        self,
        returns: pd.Series,
        title: str = "Returns Distribution"
    ) -> plt.Figure:
        """
        Plot returns distribution.
        
        Args:
            returns: Portfolio returns
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram
        ax1.hist(returns, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.4f}')
        ax1.set_title(f'{title} - Histogram', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Returns', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(returns, dist="norm", plot=ax2)
        ax2.set_title(f'{title} - Q-Q Plot', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_rolling_metrics(
        self,
        rolling_metrics: pd.DataFrame,
        title: str = "Rolling Performance Metrics"
    ) -> plt.Figure:
        """
        Plot rolling performance metrics.
        
        Args:
            rolling_metrics: DataFrame with rolling metrics
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        metrics_to_plot = ['rolling_return', 'rolling_volatility', 'rolling_sharpe', 'rolling_max_dd']
        metric_labels = ['Rolling Return', 'Rolling Volatility', 'Rolling Sharpe Ratio', 'Rolling Max Drawdown']
        
        for i, (metric, label) in enumerate(zip(metrics_to_plot, metric_labels)):
            if metric in rolling_metrics.columns:
                axes[i].plot(rolling_metrics.index, rolling_metrics[metric], linewidth=2)
                axes[i].set_title(label, fontsize=12, fontweight='bold')
                axes[i].set_xlabel('Date', fontsize=10)
                axes[i].grid(True, alpha=0.3)
                axes[i].tick_params(axis='x', rotation=45)
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def plot_trades(
        self,
        data: pd.DataFrame,
        trades: pd.DataFrame,
        title: str = "Trades on Price Chart"
    ) -> plt.Figure:
        """
        Plot trades on price chart.
        
        Args:
            data: Price data
            trades: Trades DataFrame
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot price
        ax.plot(data.index, data['close'], label='Close Price', linewidth=2, color='black')
        
        # Plot trades
        if not trades.empty:
            buy_trades = trades[trades['action'] == 'BUY']
            sell_trades = trades[trades['action'] == 'SELL']
            
            if not buy_trades.empty:
                ax.scatter(buy_trades['timestamp'], buy_trades['price'], 
                          color='green', marker='^', s=100, label='Buy', zorder=5)
            
            if not sell_trades.empty:
                ax.scatter(sell_trades['timestamp'], sell_trades['price'], 
                          color='red', marker='v', s=100, label='Sell', zorder=5)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_metrics_comparison(
        self,
        strategies_metrics: Dict[str, Dict[str, float]],
        title: str = "Strategy Comparison"
    ) -> plt.Figure:
        """
        Plot comparison of multiple strategies.
        
        Args:
            strategies_metrics: Dictionary of strategy names to metrics
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        # Convert to DataFrame
        df = pd.DataFrame(strategies_metrics).T
        
        # Select key metrics for comparison
        key_metrics = ['total_return', 'annualized_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
        available_metrics = [m for m in key_metrics if m in df.columns]
        
        if not available_metrics:
            raise ValueError("No metrics available for comparison")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, metric in enumerate(available_metrics[:4]):
            if i < len(axes):
                df[metric].plot(kind='bar', ax=axes[i], color='skyblue', edgecolor='black')
                axes[i].set_title(f'{metric.replace("_", " ").title()}', fontsize=12, fontweight='bold')
                axes[i].set_xlabel('Strategy', fontsize=10)
                axes[i].set_ylabel(metric.replace('_', ' ').title(), fontsize=10)
                axes[i].tick_params(axis='x', rotation=45)
                axes[i].grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def plot_correlation_heatmap(
        self,
        returns_data: pd.DataFrame,
        title: str = "Returns Correlation Heatmap"
    ) -> plt.Figure:
        """
        Plot correlation heatmap of returns.
        
        Args:
            returns_data: DataFrame with returns for different assets/strategies
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Calculate correlation matrix
        correlation_matrix = returns_data.corr()
        
        # Create heatmap
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, ax=ax, cbar_kws={'shrink': 0.8})
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def plot_risk_return_scatter(
        self,
        strategies_data: Dict[str, Dict[str, float]],
        title: str = "Risk vs Return"
    ) -> plt.Figure:
        """
        Plot risk vs return scatter plot.
        
        Args:
            strategies_data: Dictionary of strategy names to metrics
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Extract data
        strategies = list(strategies_data.keys())
        returns = [strategies_data[s].get('annualized_return', 0) for s in strategies]
        risks = [strategies_data[s].get('volatility', 0) for s in strategies]
        
        # Create scatter plot
        scatter = ax.scatter(risks, returns, s=100, alpha=0.7, c=range(len(strategies)), cmap='viridis')
        
        # Add labels
        for i, strategy in enumerate(strategies):
            ax.annotate(strategy, (risks[i], returns[i]), xytext=(5, 5), textcoords='offset points')
        
        ax.set_xlabel('Volatility (Risk)', fontsize=12)
        ax.set_ylabel('Annualized Return', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Strategy Index', fontsize=10)
        
        plt.tight_layout()
        return fig
