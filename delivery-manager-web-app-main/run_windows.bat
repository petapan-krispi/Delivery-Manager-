@echo off
echo ========================================
echo    Delivery Manager - Web Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if requirements are installed
echo 📦 Installing/updating required packages...
pip install -r requirements_web.txt --quiet

if errorlevel 1 (
    echo ❌ Failed to install packages
    echo Trying with --user flag...
    pip install -r requirements_web.txt --user --quiet
    if errorlevel 1 (
        echo ❌ Still failed. Please check your internet connection
        pause
        exit /b 1
    )
)

echo ✅ Packages installed successfully
echo.

REM Start the web application
echo 🚀 Starting Delivery Manager...
echo.
echo The application will open in your default web browser.
echo If it doesn't open automatically, go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py --server.port 8501 --server.headless true --server.runOnSave true --server.enableCORS false --server.enableXsrfProtection false
