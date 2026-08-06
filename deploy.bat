@echo off
cd /d "%~dp0"
set "GIT=git"
if exist "C:\Program Files\Git\cmd\git.exe" set "GIT=C:\Program Files\Git\cmd\git.exe"
if exist "C:\Program Files (x86)\Git\cmd\git.exe" set "GIT=C:\Program Files (x86)\Git\cmd\git.exe"
if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" set "GIT=%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
"%GIT%" add -A
"%GIT%" commit -m "auto deploy"
"%GIT%" push
echo.
echo ===== push done. opening Netlify credit balance ... =====
start "" "https://app.netlify.com/teams/usinyakkuk13/billing/general"
