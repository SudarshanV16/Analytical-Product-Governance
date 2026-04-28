@echo off
color 0B
echo ===================================================
echo    UNIVERSAL BI GOVERNANCE HUB BOOTSTRAP
echo ===================================================
echo.

:: Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running! Please open Docker Desktop and try again.
    pause
    exit /b
)

echo [1/3] Building Docker Container...
docker build -t bi-gov-hub .

echo [2/3] Opening Web Browser...
:: Waits 3 seconds to let Docker spin up, then opens the browser
timeout /t 3 /nobreak >nul
start http://localhost:8501

echo [3/3] Launching Application Server...
echo (Press CTRL+C in this window to safely shut down the app)
echo.
:: Runs the container and mounts the current directory
docker run --rm -p 8501:8501 -v "%cd%:/app" bi-gov-hub

pause