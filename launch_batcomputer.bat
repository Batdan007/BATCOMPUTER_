@echo off
title BATCOMPUTER_ Integrated Launcher
color 0B

echo ================================================
echo    BATCOMPUTER_ - Integrated Development Environment
echo ================================================
echo.
echo 🦇 Launching the unified BATCOMPUTER_ platform...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found! Checking version...
python --version

echo.
echo Checking BATCOMPUTER_ modules...
echo.

REM Try to run the integrated launcher first
if exist "launch_batcomputer.py" (
    echo 🚀 Launching BATCOMPUTER_ Integrated Environment...
    python launch_batcomputer.py
) else if exist "batcomputer_integrated_app.py" (
    echo 🚀 Launching BATCOMPUTER_ Integrated App directly...
    python batcomputer_integrated_app.py
) else (
    echo ERROR: BATCOMPUTER_ Integrated Application files not found!
    echo Make sure you're in the correct directory.
    echo.
    echo Expected files:
    echo - launch_batcomputer.py
    echo - batcomputer_integrated_app.py
    echo.
    pause
    exit /b 1
)

echo.
echo BATCOMPUTER_ application closed.
echo Thank you for using BATCOMPUTER_!
pause
