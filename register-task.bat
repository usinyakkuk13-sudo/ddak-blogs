@echo off
schtasks /create /tn "ddak-blog-deploy" /tr "\"%~dp0deploy.bat\"" /sc weekly /d MON /st 09:30 /f
if errorlevel 1 (
  echo Failed. Try running as administrator.
) else (
  echo.
  echo ===== Done! Auto-deploy scheduled weekly (Monday 09:30). =====
)
pause
