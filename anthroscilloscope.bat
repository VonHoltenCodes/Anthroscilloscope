@echo off
REM ============================================================
REM Anthroscilloscope Launcher for Windows
REM ============================================================

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ or run anthroscilloscope_setup.bat
    pause
    exit /b 1
)

REM Check if config exists
if not exist config.py (
    echo Warning: config.py not found!
    echo Creating from template...
    copy config_example.py config.py >nul 2>&1
    echo Please edit config.py with your oscilloscope IP address
    pause
)

REM Launch the main program
echo Starting Anthroscilloscope...
python anthroscilloscope_main.py %*

if errorlevel 1 (
    echo.
    echo Program exited with an error.
    pause
)