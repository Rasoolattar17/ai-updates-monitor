@echo off
echo 🤖 AI Updates Monitor
echo ==================

REM Check if Python is installed
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from example...
    copy env_example.txt .env
    echo ✅ Created .env file
    echo Please edit .env file with your settings before running
    pause
    exit /b 0
)

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo 📦 Installing/updating dependencies...
    py -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run the monitor
echo 🚀 Starting AI Updates Monitor...
echo Press Ctrl+C to stop
py main.py

pause