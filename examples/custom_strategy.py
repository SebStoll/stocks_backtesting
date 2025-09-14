"""
Example of creating a custom trading strategy.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_fetcher import DataFetcher
from src.strategies.base_strategy import BaseStrategy
from src.backtesting.engine import BacktestEngine
import pandas as pd
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BollingerBandsStrategy(BaseStrategy):
    """
    Custom Bollinger Bands strategy.
    
    Buys when price touches lower band and RSI is oversold.
    Sells when price touches upper band and RSI is overbought.
    """
    
    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        rsi_period: int = 14,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
        symbol: str = 'SYMBOL',
        name: Optional[str] = None
    ):
        super().__init__(name)
        self.period = period
        self.std_dev = std_dev
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.symbol = symbol
    
    def calculate_bollinger_bands(self, prices: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=self.period).mean()
        std = prices.rolling(window=self.period).std()
        
        upper_band = sma + (std * self.std_dev)
        lower_band = sma - (std * self.std_dev)
        
        return upper_band, sma, lower_band
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """Generate trading signals."""
        if len(data) < max(self.period, self.rsi_period) + 1:
            return {self.symbol: 'HOLD'}
        
        # Calculate indicators
        upper_band, middle_band, lower_band = self.calculate_bollinger_bands(data['close'])
        rsi = self.calculate_rsi(data['close'])
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        if pd.isna(current_upper) or pd.isna(current_lower) or pd.isna(current_rsi):
            return {self.symbol: 'HOLD'}
        
        # Generate signals
        if current_price <= current_lower and current_rsi < self.rsi_oversold:
            return {self.symbol: 'BUY'}
        elif current_price >= current_upper and current_rsi > self.rsi_overbought:
            return {self.symbol: 'SELL'}
        else:
            return {self.symbol: 'HOLD'}
    
    def get_parameters(self) -> Dict[str, any]:
        """Get strategy parameters."""
        return {
            'period': self.period,
            'std_dev': self.std_dev,
            'rsi_period': self.rsi_period,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'symbol': self.symbol
        }


class MeanReversionStrategy(BaseStrategy):
    """
    Custom mean reversion strategy.
    
    Buys when price is significantly below moving average.
    Sells when price is significantly above moving average.
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        symbol: str = 'SYMBOL',
        name: Optional[str] = None
    ):
        super().__init__(name)
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.symbol = symbol
    
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, str]:
        """Generate trading signals."""
        if len(data) < self.lookback_period + 1:
            return {self.symbol: 'HOLD'}
        
        # Calculate moving average and standard deviation
        sma = data['close'].rolling(window=self.lookback_period).mean()
        std = data['close'].rolling(window=self.lookback_period).std()
        
        # Get current values
        current_price = data['close'].iloc[-1]
        current_sma = sma.iloc[-1]
        current_std = std.iloc[-1]
        
        if pd.isna(current_sma) or pd.isna(current_std):
            return {self.symbol: 'HOLD'}
        
        # Calculate z-score
        z_score = (current_price - current_sma) / current_std
        
        # Generate signals
        if z_score < -self.entry_threshold:
            return {self.symbol: 'BUY'}
        elif z_score > self.exit_threshold:
            return {self.symbol: 'SELL'}
        else:
            return {self.symbol: 'HOLD'}
    
    def get_parameters(self) -> Dict[str, any]:
        """Get strategy parameters."""
        return {
            'lookback_period': self.lookback_period,
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold,
            'symbol': self.symbol
        }


def main():
    """Test custom strategies."""
    print("="*60)
    print("STOCK BACKTESTING FRAMEWORK - CUSTOM STRATEGIES")
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
    
    # Create custom strategies
    print("\n2. Creating custom strategies...")
    
    strategies = {
        'Bollinger Bands + RSI': BollingerBandsStrategy(
            period=20,
            std_dev=2.0,
            rsi_period=14,
            rsi_oversold=30,
            rsi_overbought=70,
            symbol='AAPL'
        ),
        'Mean Reversion': MeanReversionStrategy(
            lookback_period=20,
            entry_threshold=2.0,
            exit_threshold=0.5,
            symbol='AAPL'
        )
    }
    
    print(f"✓ Created {len(strategies)} custom strategies")
    
    # Run backtests
    print("\n3. Running backtests...")
    engine = BacktestEngine(initial_capital=10000, commission=0.001)
    results = {}
    
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
    
    # Display results
    print(f"\n4. Custom Strategy Results:")
    print("="*80)
    
    for name, result in results.items():
        print(f"\n{name}:")
        print("-" * 40)
        result.print_summary()
        
        # Show some trades
        trades_df = result.get_trades_dataframe()
        if not trades_df.empty:
            print(f"\nRecent Trades:")
            print(trades_df.tail(3).to_string(index=False))
        else:
            print("No trades executed")
    
    # Find best strategy
    if results:
        best_strategy = max(results.keys(), key=lambda x: results[x].metrics.get('total_return', 0))
        print(f"\n5. Best Custom Strategy: {best_strategy}")
        print(f"   Total Return: {results[best_strategy].summary()['total_return']}")
        
        # Plot best strategy
        print(f"\n6. Generating performance plot for {best_strategy}...")
        try:
            results[best_strategy].plot_performance()
            print("✓ Performance plot generated")
        except Exception as e:
            print(f"✗ Error generating plot: {e}")
    
    print("\n" + "="*60)
    print("CUSTOM STRATEGY TESTING COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    main()
