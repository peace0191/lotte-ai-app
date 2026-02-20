@echo off
echo ==================================================
echo   Lotte Tower AI Sales System - Build & Deploy
echo   (CEO Nano Banana Vibe Coding Edition)
echo ==================================================
echo.

echo [1/3] Checking Docker status...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not running.
    echo Please install Docker Desktop for Windows.
    pause
    exit /b
)

echo [2/3] Building and starting containers via Docker Compose...
docker-compose up -d --build

echo.
echo [3/3] Deployment complete!
echo.
echo ==================================================
echo   PORTAL PAGE  : http://localhost
echo   AI SYSTEM    : http://localhost:8501
echo ==================================================
echo.
echo Press any key to open the Portal page...
pause >nul
start http://localhost
