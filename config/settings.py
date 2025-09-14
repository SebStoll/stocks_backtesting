"""
Configuration settings for the backtesting framework.
"""

import os
from typing import Dict, Any

# Data settings
DATA_SETTINGS = {
    'default_symbol': 'AAPL',
    'default_start_date': '2020-01-01',
    'default_end_date': '2023-01-01',
    'default_interval': '1d',
    'cache_enabled': True,
    'cache_size_limit': 100,  # MB
    'default_data_source': 'yahoo_finance'
}

# Data source settings
DATA_SOURCE_SETTINGS = {
    'yahoo_finance': {
        'timeout': 10,
        'max_retries': 3,
        'retry_delay': 1.0
    }
}

# Backtesting settings
BACKTEST_SETTINGS = {
    'default_initial_capital': 10000.0,
    'default_benchmark_symbol': None,
    'risk_free_rate': 0.02,  # 2% annual
    'trading_days_per_year': 252
}

# Trading costs settings
TRADING_COSTS = {
    'cost_type': 'fixed',  # 'fixed' or 'percentage'
    'fixed_cost_per_trade': 1.0,  # Fixed cost in EUR/USD per trade
    'percentage_cost_per_trade': 0.002,  # 0.2% of trade value
    'apply_to_buy': True,  # Apply costs to buy trades
    'apply_to_sell': True,  # Apply costs to sell trades
    'currency': 'EUR'  # Currency for fixed costs
}

# Tax settings
TAX_SETTINGS = {
    'tax_rate': 0.26375,  # 25% tax rate on profits
    'apply_immediately': True,  # Apply tax immediately on profitable trades
    'tax_on_realized_gains_only': True,  # Only tax realized gains (not unrealized)
    'tax_free_threshold': 0.0,  # Tax-free threshold amount
    'currency': 'EUR'  # Currency for tax calculations
}

# Strategy settings - Currently unused, strategies use hardcoded defaults
# STRATEGY_SETTINGS = {
#     'default_short_window': 20,
#     'default_long_window': 50,
#     'default_rsi_period': 14,
#     'default_rsi_oversold': 30.0,
#     'default_rsi_overbought': 70.0,
#     'default_macd_fast': 12,
#     'default_macd_slow': 26,
#     'default_macd_signal': 9
# }

# Visualization settings - Only style is used, others are hardcoded
PLOT_SETTINGS = {
    'style': 'seaborn-v0_8'
    # 'default_figsize': (12, 8),  # Unused - hardcoded in plots.py
    # 'color_palette': 'husl',     # Unused - hardcoded in plots.py
    # 'dpi': 100,                   # Unused
    # 'save_plots': False,          # Unused
    # 'plot_format': 'png'          # Unused
}

# Logging settings - Currently unused, logging is hardcoded in files
# LOGGING_SETTINGS = {
#     'level': 'INFO',
#     'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     'file_logging': False,
#     'log_file': 'backtesting.log'
# }

# API settings - Duplicate of DATA_SOURCE_SETTINGS, currently unused
# API_SETTINGS = {
#     'yfinance_timeout': 10,
#     'max_retries': 3,
#     'retry_delay': 1.0
# }

# Performance settings - Currently unused, not implemented
# PERFORMANCE_SETTINGS = {
#     'parallel_processing': True,
#     'max_workers': 4,
#     'memory_limit_mb': 1000
# }

def get_setting(category: str, key: str, default: Any = None) -> Any:
    """
    Get a configuration setting.
    
    Args:
        category: Configuration category
        key: Setting key
        default: Default value if not found
        
    Returns:
        Setting value
    """
    settings_map = {
        'data': DATA_SETTINGS,
        'data_source': DATA_SOURCE_SETTINGS,
        'backtest': BACKTEST_SETTINGS,
        'trading_costs': TRADING_COSTS,
        'tax': TAX_SETTINGS,
        'plot': PLOT_SETTINGS
        # 'strategy': STRATEGY_SETTINGS,  # Commented out - unused
        # 'logging': LOGGING_SETTINGS,   # Commented out - unused
        # 'api': API_SETTINGS,           # Commented out - unused
        # 'performance': PERFORMANCE_SETTINGS  # Commented out - unused
    }
    
    if category not in settings_map:
        return default
    
    return settings_map[category].get(key, default)

def update_setting(category: str, key: str, value: Any) -> bool:
    """
    Update a configuration setting.
    
    Args:
        category: Configuration category
        key: Setting key
        value: New value
        
    Returns:
        True if successful, False otherwise
    """
    settings_map = {
        'data': DATA_SETTINGS,
        'data_source': DATA_SOURCE_SETTINGS,
        'backtest': BACKTEST_SETTINGS,
        'trading_costs': TRADING_COSTS,
        'tax': TAX_SETTINGS,
        'plot': PLOT_SETTINGS
        # 'strategy': STRATEGY_SETTINGS,  # Commented out - unused
        # 'logging': LOGGING_SETTINGS,   # Commented out - unused
        # 'api': API_SETTINGS,           # Commented out - unused
        # 'performance': PERFORMANCE_SETTINGS  # Commented out - unused
    }
    
    if category not in settings_map:
        return False
    
    settings_map[category][key] = value
    return True
