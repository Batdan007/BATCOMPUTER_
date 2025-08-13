@echo off
title BATCOMPUTER Voice Commander
echo.
echo 🎭 BATCOMPUTER Voice Commander - Starting...
echo.
echo Make sure your microphone is connected and working!
echo.
echo Press Ctrl+C to exit
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\Activate.ps1" (
    echo Activating virtual environment...
    powershell -ExecutionPolicy Bypass -File ".venv\Scripts\Activate.ps1"
    python BATCOMPUTER_voice_commander.py
) else (
    echo No virtual environment found, using system Python...
    python BATCOMPUTER_voice_commander.py
)

echo.
echo BATCOMPUTER Voice Commander has exited.
pause
