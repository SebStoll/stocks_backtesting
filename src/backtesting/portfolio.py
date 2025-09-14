"""
Portfolio management for backtesting.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Portfolio:
    """
    Manages portfolio state during backtesting.
    """
    
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001):
        """
        Initialize portfolio.
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate per trade (as decimal)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        
        # Portfolio state
        self.positions = {}  # {symbol: shares}
        self.portfolio_value = initial_capital
        self.trades = []
        self.portfolio_history = []
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_commission_paid = 0.0
        
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
        cost = shares * price * (1 + self.commission)
        return cost <= self.cash
    
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
        
        cost = shares * price * (1 + self.commission)
        commission_paid = shares * price * self.commission
        
        # Update portfolio
        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + shares
        self.total_commission_paid += commission_paid
        
        # Record trade
        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'cost': cost,
            'commission': commission_paid,
            'cash_after': self.cash,
            'portfolio_value': self.get_total_value({symbol: price})
        }
        self.trades.append(trade)
        self.total_trades += 1
        
        logger.info(f"Bought {shares} shares of {symbol} at {price:.2f}")
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
        
        proceeds = shares * price * (1 - self.commission)
        commission_paid = shares * price * self.commission
        
        # Update portfolio
        self.cash += proceeds
        self.positions[symbol] -= shares
        self.total_commission_paid += commission_paid
        
        # Record trade
        trade = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'SELL',
            'shares': shares,
            'price': price,
            'proceeds': proceeds,
            'commission': commission_paid,
            'cash_after': self.cash,
            'portfolio_value': self.get_total_value({symbol: price})
        }
        self.trades.append(trade)
        self.total_trades += 1
        
        # Track winning/losing trades
        if symbol in self.positions and self.positions[symbol] == 0:
            # Calculate P&L for this position
            buy_trades = [t for t in self.trades if t['symbol'] == symbol and t['action'] == 'BUY']
            sell_trades = [t for t in self.trades if t['symbol'] == symbol and t['action'] == 'SELL']
            
            if buy_trades and sell_trades:
                total_buy_cost = sum(t['cost'] for t in buy_trades)
                total_sell_proceeds = sum(t['proceeds'] for t in sell_trades)
                pnl = total_sell_proceeds - total_buy_cost
                
                if pnl > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1
        
        logger.info(f"Sold {shares} shares of {symbol} at {price:.2f}")
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
            'total_commission_paid': self.total_commission_paid
        }
        self.portfolio_history.append(portfolio_snapshot)
    
    def get_position_size(self, symbol: str) -> int:
        """Get current position size for symbol."""
        return self.positions.get(symbol, 0)
    
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
        self.total_commission_paid = 0.0
