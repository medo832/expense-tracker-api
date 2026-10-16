@echo off
cd /d "%~dp0"
echo ==================================================
echo   STEP 1 - prepare what goes to GitHub
echo ==================================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo No git repo here yet - running git init
  git init
  echo.
)

echo Removing private and non-code files from git
echo (they stay on your disk - only git forgets them)
git rm -r --cached "Claude outputs" >nul 2>&1
git rm --cached mentor-review.md >nul 2>&1
git rm --cached add.py >nul 2>&1
git rm --cached expenser.json >nul 2>&1
git rm --cached design.docx >nul 2>&1
git rm --cached "api/how to test.docx" >nul 2>&1
git rm -r --cached backend >nul 2>&1
echo.

git add -A
echo ==================================================
echo   THIS is what will be published:
echo ==================================================
git status --short
echo ==================================================
echo.
echo Read the list. You must NOT see any of these:
echo    .venv      expenses.db      mentor-review.md
echo    Claude outputs/             *.docx
echo.
echo If the list is clean, run:  git-push.bat
echo.
pause
