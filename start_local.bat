@echo off
color 0B
echo ===================================================
echo   🚀 UNIVERSAL BI GOVERNANCE HUB BOOTSTRAP
echo ===================================================
echo.

:: Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running! Please open Docker Desktop and try again.
    pause
    exit /b
)

echo [1/4] Building Docker Container...
docker build -t bi-gov-hub .

echo [2/4] Initializing Mock Database...
:: This runs the python script INSIDE docker, but saves the .db file back to your Windows folder!
docker run --rm -v "%cd%:/app" bi-gov-hub python app/init_db.py

echo [3/4] Opening Web Browser...
:: Increased timeout to 6 seconds so the container has time to start
timeout /t 6 /nobreak >nul
start http://localhost:8501

echo [4/4] Launching Application Server...
echo (Press CTRL+C in this window to safely shut down the app)
echo.
:: Runs the container and mounts the current directory
docker run --rm -p 8501:8501 -v "%cd%:/app" bi-gov-hub

pause