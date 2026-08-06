@echo off
cd /d "%~dp0"
set "GIT=git"
if exist "C:\Program Files\Git\cmd\git.exe" set "GIT=C:\Program Files\Git\cmd\git.exe"
if exist "C:\Program Files (x86)\Git\cmd\git.exe" set "GIT=C:\Program Files (x86)\Git\cmd\git.exe"
if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" set "GIT=%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
echo Using Git: %GIT%
"%GIT%" --version
if errorlevel 1 goto nogit
"%GIT%" init
"%GIT%" config user.email "usinyakkuk13@gmail.com"
"%GIT%" config user.name "ddak blog"
"%GIT%" add -A
"%GIT%" commit -m "first commit"
"%GIT%" branch -M main
"%GIT%" remote remove origin 2>nul
"%GIT%" remote add origin https://github.com/usinyakkuk13-sudo/ddak-blogs.git
"%GIT%" push -u origin main
echo.
echo ===== DONE. deploy.bat now handles daily auto-deploy. =====
pause
exit /b 0
:nogit
echo Git not found. Install from https://git-scm.com/download/win then retry.
pause
