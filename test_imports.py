"""
Test script to verify all imports work correctly.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports."""
    print("Testing imports...")
    
    try:
        from src.data.data_fetcher import DataFetcher
        print("✓ DataFetcher imported successfully")
    except Exception as e:
        print(f"✗ DataFetcher import failed: {e}")
        return False
    
    try:
        from src.strategies.base_strategy import BaseStrategy
        print("✓ BaseStrategy imported successfully")
    except Exception as e:
        print(f"✗ BaseStrategy import failed: {e}")
        return False
    
    try:
        from src.strategies.moving_average import MovingAverageStrategy
        print("✓ MovingAverageStrategy imported successfully")
    except Exception as e:
        print(f"✗ MovingAverageStrategy import failed: {e}")
        return False
    
    try:
        from src.backtesting.portfolio import Portfolio
        print("✓ Portfolio imported successfully")
    except Exception as e:
        print(f"✗ Portfolio import failed: {e}")
        return False
    
    try:
        from src.backtesting.engine import BacktestEngine
        print("✓ BacktestEngine imported successfully")
    except Exception as e:
        print(f"✗ BacktestEngine import failed: {e}")
        return False
    
    try:
        from src.metrics.performance import PerformanceMetrics
        print("✓ PerformanceMetrics imported successfully")
    except Exception as e:
        print(f"✗ PerformanceMetrics import failed: {e}")
        return False
    
    try:
        from src.visualization.plots import BacktestPlots
        print("✓ BacktestPlots imported successfully")
    except Exception as e:
        print(f"✗ BacktestPlots import failed: {e}")
        return False
    
    print("\n✓ All imports successful!")
    return True

if __name__ == "__main__":
    test_imports()
