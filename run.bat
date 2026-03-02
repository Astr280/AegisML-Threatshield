@echo off
echo ========================================
echo Starting Malware Detection System...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if upload.csv exists
if not exist "upload.csv" (
    echo WARNING: Dataset file 'upload.csv' not found!
    echo Generating dataset...
    python generate_dataset.py
)

echo Starting Flask application...
echo.
echo The application will be available at: http://127.0.0.1:5000/
echo.
echo Login credentials:
echo   Username: admin
echo   Password: admin
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
