@echo off
title App Program Writer Launcher
color 0A

echo ================================================
echo    App Program Writer - Professional Code Editor
echo ================================================
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
echo Launching App Program Writer...
echo.

REM Try to run the launcher script first
if exist "launch_app_writer.py" (
    python launch_app_writer.py
) else if exist "app_program_writer.py" (
    python app_program_writer.py
) else (
    echo ERROR: App Program Writer files not found!
    echo Make sure you're in the correct directory.
    echo.
    pause
    exit /b 1
)

echo.
echo Application closed.
pause
