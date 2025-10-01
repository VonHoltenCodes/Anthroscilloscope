@echo off
REM ============================================================
REM Anthroscilloscope Advanced Text GUI Launcher for Windows
REM Launches Phase 4 Advanced GUI with Effects
REM ============================================================

cd /d "%~dp0"

echo ========================================================================
echo ANTHROSCILLOSCOPE - Advanced Lissajous Text Generator (Phase 4)
echo ========================================================================
echo.
echo Launching Advanced GUI with Effects...
echo Features: Rotation, Scaling, 3D, Shadow, Wave effects
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ or run anthroscilloscope_setup.bat
    pause
    exit /b 1
)

REM Check matplotlib and numpy
python -c "import matplotlib, numpy" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Required packages not found
    echo Installing dependencies...
    call anthroscilloscope_setup.bat
)

REM Launch Advanced GUI
python text_gui_advanced.py %*

if errorlevel 1 (
    echo.
    echo Advanced GUI exited with an error.
    pause
)
