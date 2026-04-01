@echo off
cd /d "%~dp0"
git add -A
git diff --cached --quiet
if %errorlevel%==0 (
    echo Nessuna modifica da pushare.
    pause
    exit /b
)
set /p msg="Messaggio commit: "
git commit -m "%msg%"
git push
echo.
echo Push completato!
pause
