@echo off
REM ============================================================
REM   PlotPilot - AI Novel Platform Launcher (Windows)
REM ============================================================
REM   Usage:
REM     start.bat          auto mode (recommended, double-click)
REM     start.bat force    force kill stale backend before start
REM
REM   Requires:
REM     - Python 3.10+ (with tkinter)
REM     - Node.js 20+  (for frontend)
REM ============================================================

setlocal enabledelayedexpansion

REM Switch to script directory
cd /d "%~dp0"

set "MODE=%1"
if "%MODE%"=="" set "MODE=auto"

REM ====== Ensure required directories ======
if not exist logs mkdir logs
if not exist data\chromadb mkdir data\chromadb
if not exist data\logs mkdir data\logs

REM ====== Locate Python (prefer .venv, then py launcher, then python) ======
set "PYTHON_EXE="

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    echo   [INFO]  Using venv Python: !PYTHON_EXE!
    goto python_found
)

where py >nul 2>nul
if %errorlevel%==0 (
    for /f "tokens=*" %%i in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%i"
    if defined PYTHON_EXE (
        echo   [INFO]  Using py launcher: !PYTHON_EXE!
        goto python_found
    )
)

where python >nul 2>nul
if %errorlevel%==0 (
    for /f "tokens=*" %%i in ('where python') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
    echo   [INFO]  Using system Python: !PYTHON_EXE!
    goto python_found
)

echo   [ERR ]  Python 3.10+ not found. Install from:
echo           https://www.python.org/downloads/windows/
exit /b 1

:python_found

REM ====== force mode: kill stale backend ======
if /I "%MODE%"=="force" (
    echo   [INFO]  Force mode: killing processes on ports 8005/8006...
    for %%P in (8005 8006) do (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%P " ^| findstr "LISTENING"') do (
            taskkill /PID %%a /F >nul 2>nul
            echo   [ OK ]  Killed PID %%a on port %%P
        )
    )
)

echo.
echo   +--------------------------------------+
echo   ^|  Starting PlotPilot...               ^|
echo   +--------------------------------------+
echo.

REM ====== Launch GUI hub in background ======
start "PlotPilot Hub" /B "!PYTHON_EXE!" -u scripts\install\hub.py %MODE% ^
    1^>logs\hub_stdout.log 2^>logs\hub_error.log

timeout /T 1 /NOBREAK >nul
echo   [ OK ]  PlotPilot launched. Log: logs\hub_error.log
echo   [INFO]  Close this window when you are done.

endlocal
exit /b 0
