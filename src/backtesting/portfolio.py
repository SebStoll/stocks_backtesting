"""
Portfolio management for backtesting.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import get_setting

logger = logging.getLogger(__name__)


class Portfolio:
    """
    Manages portfolio state during backtesting.
    """
    
    def __init__(
        self, 
        initial_capital: float = 10000.0, 
        trading_costs_config: Optional[Dict] = None,
        tax_config: Optional[Dict] = None
    ):
        """
        Initialize portfolio.
        
        Args:
            initial_capital: Starting capital
            trading_costs_config: Trading costs configuration dict
            tax_config: Tax configuration dict
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        
        # Load trading costs configuration
        if trading_costs_config is None:
            self.trading_costs = {
                'cost_type': get_setting('trading_costs', 'cost_type', 'percentage'),
                'fixed_cost_per_trade': get_setting('trading_costs', 'fixed_cost_per_trade', 10.0),
                'percentage_cost_per_trade': get_setting('trading_costs', 'percentage_cost_per_trade', 0.002),
                'apply_to_buy': get_setting('trading_costs', 'apply_to_buy', True),
                'apply_to_sell': get_setting('trading_costs', 'apply_to_sell', True),
                'currency': get_setting('trading_costs', 'currency', 'EUR')
            }
        else:
            self.trading_costs = trading_costs_config
        
        # Load tax configuration
        if tax_config is None:
            self.tax_config = {
                'tax_rate': get_setting('tax', 'tax_rate', 0.25),
                'apply_immediately': get_setting('tax', 'apply_immediately', True),
                'tax_on_realized_gains_only': get_setting('tax', 'tax_on_realized_gains_only', True),
                'tax_free_threshold': get_setting('tax', 'tax_free_threshold', 0.0),
                'currency': get_setting('tax', 'currency', 'EUR')
            }
        else:
            self.tax_config = tax_config
        
        # Portfolio state
        self.positions = {}  # {symbol: shares}
        self.portfolio_value = initial_capital
        self.trades = []
        self.portfolio_history = []
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_trading_costs_paid = 0.0
        self.total_taxes_paid = 0.0
        
        # Position tracking for tax calculations
        self.position_cost_basis = {}  # {symbol: total_cost_basis}
        self.position_shares = {}  # {symbol: total_shares}
        
    def get_position_value(self, symbol: str, current_price: float) -> float:
        """Get current value of position in symbol."""
        return self.positions.get(symbol, 0) * current_price
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Get total portfolio value."""
        cash_value = self.cash
        position_value = sum(
            self.get_position_value(symbol, price) 
            for symbol, price in current_prices.items()
        )
        return cash_value + position_value
    
    def can_buy(self, symbol: str, shares: int, price: float) -> bool:
        """Check if we can afford to buy shares."""
        trade_value = shares * price
        trading_cost = self.calculate_trading_cost(trade_value, 'BUY')
        total_cost = trade_value + trading_cost
        return total_cost <= self.cash
    
    def can_sell(self, symbol: str, shares: int) -> bool:
        """Check if we have enough shares to sell."""
        return self.positions.get(symbol, 0) >= shares
    
    def buy(self, symbol: str, shares: int, price: float, timestamp: datetime) -> bool:
        """
        Buy shares of a symbol.
        
        Args:
            symbol: Stock symbol
            shares: Number of shares to buy
            price: Price per share
            timestamp: Trade timestamp
            
        Returns:
            True if successful, False otherwise
        """
        if not self.can_buy(symbol, shares, price):
            logger.warning(f"Cannot buy {shares} shares of {symbol} at {price}")
            return False
        
        trade_value = shares * price
        trading_cost = self.calculate_trading_cost(trade_value, 'BUY')
        total_cost = trade_value + trading_cost
        
        # Update portfolio
        self.cash -= total_cost
        self.positions[symbol] = self.positions.get(symbol, 0) + shares
        
        # Update cost basis for tax calculations
        if symbol not in self.position_cost_basis:
            self.position_cost_basis[symbol] = 0.0
            self.position_shares[symbol] = 0
        
        self.position_cost_basis[symbol] += trade_value + trading_cost
        self.position_shares[symbol] += shares
        
        # Update tracking
        self.total_trading_costs_paid += trading_cost
        
        # Record trade
        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'trade_value': trade_value,
            'commission': trading_cost,
            'trading_cost': trading_cost,
            'total_cost': total_cost,
            'cash_after': self.cash,
            'portfolio_value': self.get_total_value({symbol: price})
        }
        self.trades.append(trade)
        self.total_trades += 1
        
        logger.info(f"Bought {shares} shares of {symbol} at {price:.2f} (Total cost: {total_cost:.2f})")
        return True
    
    def sell(self, symbol: str, shares: int, price: float, timestamp: datetime) -> bool:
        """
        Sell shares of a symbol.
        
        Args:
            symbol: Stock symbol
            shares: Number of shares to sell
            price: Price per share
            timestamp: Trade timestamp
            
        Returns:
            True if successful, False otherwise
        """
        if not self.can_sell(symbol, shares):
            logger.warning(f"Cannot sell {shares} shares of {symbol}")
            return False
        
        trade_value = shares * price
        trading_cost = self.calculate_trading_cost(trade_value, 'SELL')
        gross_proceeds = trade_value - trading_cost
        
        # Calculate profit/loss for tax purposes
        if symbol in self.position_cost_basis and self.position_shares[symbol] > 0:
            # Calculate average cost basis per share
            avg_cost_per_share = self.position_cost_basis[symbol] / self.position_shares[symbol]
            cost_basis_for_sale = shares * avg_cost_per_share
            profit = gross_proceeds - cost_basis_for_sale
            
            # Calculate and apply tax
            tax_amount = self.calculate_tax(profit)
            net_proceeds = gross_proceeds - tax_amount
            
            # Update cost basis (reduce by proportional amount)
            self.position_cost_basis[symbol] -= cost_basis_for_sale
            self.position_shares[symbol] -= shares
            
            # Track winning/losing trades
            if profit > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
        else:
            # No cost basis available (shouldn't happen in normal operation)
            net_proceeds = gross_proceeds
            profit = 0.0
            tax_amount = 0.0
            logger.warning(f"No cost basis available for {symbol} sale")
        
        # Update portfolio
        self.cash += net_proceeds
        self.positions[symbol] -= shares
        
        # Update tracking
        self.total_trading_costs_paid += trading_cost
        self.total_taxes_paid += tax_amount
        
        # Record trade
        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'SELL',
            'shares': shares,
            'price': price,
            'trade_value': trade_value,
            'commission': trading_cost,
            'trading_cost': trading_cost,
            'gross_proceeds': gross_proceeds,
            'profit': profit,
            'tax_paid': tax_amount,
            'net_proceeds': net_proceeds,
            'cash_after': self.cash,
            'portfolio_value': self.get_total_value({symbol: price})
        }
        self.trades.append(trade)
        self.total_trades += 1
        
        logger.info(f"Sold {shares} shares of {symbol} at {price:.2f} (Net proceeds: {net_proceeds:.2f}, Tax: {tax_amount:.2f})")
        return True
    
    def update_portfolio_value(self, current_prices: Dict[str, float], timestamp: datetime):
        """Update portfolio value and record in history."""
        self.portfolio_value = self.get_total_value(current_prices)
        
        portfolio_snapshot = {
            'timestamp': timestamp,
            'cash': self.cash,
            'positions': self.positions.copy(),
            'portfolio_value': self.portfolio_value,
            'total_trades': self.total_trades,
            'total_trading_costs_paid': self.total_trading_costs_paid,
            'total_taxes_paid': self.total_taxes_paid
        }
        self.portfolio_history.append(portfolio_snapshot)
    
    def get_position_size(self, symbol: str) -> int:
        """Get current position size for symbol."""
        return self.positions.get(symbol, 0)
    
    def calculate_trading_cost(self, trade_value: float, action: str) -> float:
        """
        Calculate trading cost for a trade.
        
        Args:
            trade_value: Value of the trade (shares * price)
            action: 'BUY' or 'SELL'
            
        Returns:
            Trading cost amount
        """
        if action == 'BUY' and not self.trading_costs['apply_to_buy']:
            return 0.0
        if action == 'SELL' and not self.trading_costs['apply_to_sell']:
            return 0.0
        
        if self.trading_costs['cost_type'] == 'fixed':
            return self.trading_costs['fixed_cost_per_trade']
        elif self.trading_costs['cost_type'] == 'percentage':
            return trade_value * self.trading_costs['percentage_cost_per_trade']
        else:
            return 0.0
    
    def calculate_tax(self, profit: float) -> float:
        """
        Calculate tax on profit.
        
        Args:
            profit: Profit amount (can be negative for losses)
            
        Returns:
            Tax amount to be paid
        """
        if not self.tax_config['apply_immediately']:
            return 0.0
        
        if profit <= self.tax_config['tax_free_threshold']:
            return 0.0
        
        taxable_profit = profit - self.tax_config['tax_free_threshold']
        return max(0.0, taxable_profit * self.tax_config['tax_rate'])
    
    def get_cash_ratio(self) -> float:
        """Get ratio of cash to total portfolio value."""
        return self.cash / self.portfolio_value if self.portfolio_value > 0 else 1.0
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        if not self.trades:
            return pd.DataFrame()
        return pd.DataFrame(self.trades)
    
    def get_portfolio_history_dataframe(self) -> pd.DataFrame:
        """Get portfolio history as DataFrame."""
        if not self.portfolio_history:
            return pd.DataFrame()
        return pd.DataFrame(self.portfolio_history)
    
    def reset(self):
        """Reset portfolio to initial state."""
        self.cash = self.initial_capital
        self.positions = {}
        self.portfolio_value = self.initial_capital
        self.trades = []
        self.portfolio_history = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_trading_costs_paid = 0.0
        self.total_taxes_paid = 0.0
        self.position_cost_basis = {}
        self.position_shares = {}
