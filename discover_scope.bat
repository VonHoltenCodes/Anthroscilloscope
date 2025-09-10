@echo off
REM ============================================================
REM Oscilloscope Discovery Tool for Windows
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo         RIGOL OSCILLOSCOPE DISCOVERY TOOL
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

REM Run discovery
echo Searching for oscilloscopes on the network...
echo This may take up to 30 seconds...
echo.

python device_discovery.py

echo.
pause