@echo off

cd /d "%~dp0"

if not exist ".venv" (
    echo.
    echo Virtual environment not found.
    echo.
    pause
    exit /b
)

call .venv\Scripts\activate

echo.
echo Starting Finance Platform...
echo.

python flet_app.py

if errorlevel 1 (
    echo.
    echo Application crashed.
    echo.
)

pause