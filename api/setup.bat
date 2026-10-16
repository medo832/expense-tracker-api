@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo ===============================================
echo   Expense Tracker API  -  SETUP
echo ===============================================
echo.

set "PY="
py -3.11 --version >nul 2>&1 && set "PY=py -3.11"
if not defined PY ( py --version >nul 2>&1 && set "PY=py" )
if not defined PY ( python --version >nul 2>&1 && set "PY=python" )
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"

if not defined PY (
  echo [X] Python was not found.
  echo     Install Python 3.11 from python.org and tick "Add python.exe to PATH".
  goto :fail
)

echo [1/3] Using Python: %PY%
%PY% --version
echo.

if exist ".venv\Scripts\python.exe" (
  echo [2/3] Virtual environment already exists - skipping.
) else (
  echo [2/3] Creating virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 goto :fail
)
echo.

if not exist ".venv\Scripts\python.exe" (
  echo [X] .venv was not created properly.
  goto :fail
)

echo [3/3] Installing packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :fail
echo.
echo ===============================================
echo   SETUP DONE
echo   Now double-click:  run.bat
echo ===============================================
pause
exit /b 0

:fail
echo.
echo ===============================================
echo   SETUP FAILED
echo   Copy everything above and send it to Claude.
echo ===============================================
pause
exit /b 1
