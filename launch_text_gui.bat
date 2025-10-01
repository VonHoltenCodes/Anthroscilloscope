@echo off
REM ============================================================
REM Anthroscilloscope Text GUI Launcher for Windows
REM Launches Phase 3 Standard Text Rendering GUI
REM ============================================================

cd /d "%~dp0"

echo ========================================================================
echo ANTHROSCILLOSCOPE - Lissajous Text Generator
echo ========================================================================
echo.
echo Launching Phase 3 Standard GUI...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ or run anthroscilloscope_setup.bat
    pause
    exit /b 1
)

REM Check matplotlib
python -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo WARNING: matplotlib not found
    echo Installing dependencies...
    call anthroscilloscope_setup.bat
)

REM Launch GUI
python text_gui.py %*

if errorlevel 1 (
    echo.
    echo GUI exited with an error.
    pause
)
