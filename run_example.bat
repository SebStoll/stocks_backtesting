@echo off
echo Starting Stock Backtesting Example...
echo.

REM Try different Python commands
echo Trying python...
python examples/simple_strategy_fixed.py
if %errorlevel% equ 0 goto :success

echo.
echo Trying py...
py examples/simple_strategy_fixed.py
if %errorlevel% equ 0 goto :success

echo.
echo Trying python3...
python3 examples/simple_strategy_fixed.py
if %errorlevel% equ 0 goto :success

echo.
echo Python not found. Please install Python 3.8+ and try again.
echo You can download Python from: https://www.python.org/downloads/
pause
exit /b 1

:success
echo.
echo Example completed successfully!
pause
