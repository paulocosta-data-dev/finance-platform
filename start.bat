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

python flet_app.py

pause