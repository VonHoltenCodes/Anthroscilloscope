@echo off
REM ============================================================
REM Anthroscilloscope Test Suite for Windows
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo           ANTHROSCILLOSCOPE TEST SUITE
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

REM Run test suite
echo Running quick tests...
python test_suite.py --quick %*

echo.
echo Test suite complete.
pause