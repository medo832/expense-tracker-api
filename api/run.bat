@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [X] No virtual environment found.
  echo     Run setup.bat first.
  pause
  exit /b 1
)
echo Starting the server...
echo Open this in your browser:  http://127.0.0.1:8000/docs
echo Press CTRL+C here to stop it.
echo.
start "" http://127.0.0.1:8000/docs
".venv\Scripts\python.exe" -m uvicorn main:app --reload
pause
