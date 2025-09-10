@echo off
REM ============================================================
REM Anthroscilloscope Setup Script for Windows
REM ============================================================

echo.
echo ============================================================
echo           ANTHROSCILLOSCOPE SETUP (WINDOWS)
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10 or later
    echo.
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install required packages
echo Installing required packages...
echo.

echo [1/9] Installing pyvisa...
pip install pyvisa

echo [2/9] Installing pyvisa-py...
pip install pyvisa-py

echo [3/9] Installing pyusb...
pip install pyusb

echo [4/9] Installing pyserial...
pip install pyserial

echo [5/9] Installing matplotlib...
pip install matplotlib

echo [6/9] Installing numpy...
pip install numpy

echo [7/9] Installing scipy...
pip install scipy

echo [8/9] Installing h5py...
pip install h5py

echo [9/9] Installing pandas...
pip install pandas

echo.
echo Optional: Installing zeroconf for mDNS discovery...
pip install zeroconf

echo.
echo ============================================================
echo Creating launcher script...
echo ============================================================

REM Create the main launcher
echo @echo off > anthroscilloscope.bat
echo cd /d "%%~dp0" >> anthroscilloscope.bat
echo python anthroscilloscope_main.py %%* >> anthroscilloscope.bat

echo Launcher created: anthroscilloscope.bat
echo.

REM Create config file if it doesn't exist
if not exist config.py (
    echo Creating config.py from template...
    copy config_example.py config.py >nul 2>&1
    if errorlevel 1 (
        echo Warning: Could not create config.py
        echo Please copy config_example.py to config.py manually
    ) else (
        echo Config file created. Please edit config.py with your oscilloscope IP address.
    )
) else (
    echo Config.py already exists.
)

echo.
echo ============================================================
echo                    SETUP COMPLETE!
echo ============================================================
echo.
echo To start Anthroscilloscope, run: anthroscilloscope.bat
echo.
echo First time setup:
echo   1. Edit config.py with your oscilloscope IP address
echo   2. Run: discover_scope.bat to find your oscilloscope
echo   3. Run: anthroscilloscope.bat to start the main program
echo.
pause