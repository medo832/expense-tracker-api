@echo off
cd /d "%~dp0"
echo ==================================================
echo   STEP 2 - commit and push
echo ==================================================
echo.

for /f "delims=" %%i in (git config --global user.email) do set EMAIL=%%i
if "%EMAIL%"=="" (
  echo Setting your git identity...
  git config --global user.name "Mohamed Elkenawi"
  git config --global user.email "moel832005@gmail.com"
  echo.
)

set "URL="
set /p URL=Paste your GitHub repo URL and press Enter: 
if "%URL%"=="" (
  echo No URL given. Stopping.
  pause
  exit /b 1
)
echo.

git commit -m "Expense Tracker API: FastAPI + SQLite, design-first"
git branch -M main
git remote remove origin >nul 2>&1
git remote add origin %URL%
echo.
echo Pushing... a browser window may open to sign in to GitHub.
git push -u origin main
echo.
echo ==================================================
echo   Done. Open your repo URL in the browser.
echo ==================================================
pause
