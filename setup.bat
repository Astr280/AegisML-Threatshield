@echo off
echo ========================================
echo Malware Detection System - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.10.9 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

echo Installing required packages...
echo.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Dependencies installed successfully!
echo ========================================
echo.

echo Generating dataset...
python generate_dataset.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to generate dataset!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To run the application, execute: run.bat
echo Or manually run: python app.py
echo.
pause
