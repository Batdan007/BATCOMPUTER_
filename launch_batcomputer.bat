@echo off
title BATCOMPUTER_
color 0B

REM Ensure Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Launch the integrated app
python "%~dp0batcomputer_integrated_app.py"
pause
