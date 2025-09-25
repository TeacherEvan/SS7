@echo off
REM SS6 Game Updater - Windows Batch Script
REM Note: %errorlevel% is a standard Windows batch variable for exit codes
title SS6 Game Updater
echo.
echo 🎮 SS6 Super Student Game - Quick Update
echo =======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if requests module is available
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing required update dependencies...
    python -m pip install requests --quiet
    if %errorlevel% neq 0 (
        echo ❌ Failed to install required packages
        echo    Please check your internet connection
        pause
        exit /b 1
    )
)

REM Run the updater
python update_game.py
pause