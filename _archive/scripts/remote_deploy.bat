@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title LOTTE AI - ULTRA FAST DEPLOY (PRODUCTION MASTER v5.5.6 EXCELLENT)

REM ===== AWS 설정 =====
set SERVER_IP=43.200.87.22
set USER=bitnami
set KEY_NAME=LAMP_KEY.pem
set KEY_PATH=%~dp0%KEY_NAME%
set REMOTE_DIR=/home/bitnami/lotte_ai_docker

echo [1/6] Setting SSH Key Permissions...
icacls "%KEY_PATH%" /inheritance:r >nul 2>&1
icacls "%KEY_PATH%" /grant:r "%USERNAME%:R" >nul 2>&1

echo [2/6] Cleaning and Packaging (Fail-fast)...
if exist "deploy.tgz" del /f /q deploy.tgz
tar -czf deploy.tgz pages scripts services data assets videos app.py Dockerfile docker-compose.yml requirements.txt index.html style.css LAMP_KEY.pem .dockerignore
if %errorlevel% neq 0 (
    echo [ERROR] Packaging failed. Make sure tar is in your PATH.
    pause
    exit /b 1
)

echo [3/6] Uploading setup script and project...
scp -o StrictHostKeyChecking=no -i "%KEY_PATH%" "%~dp0scripts\setup_dns.sh" %USER%@%SERVER_IP%:/tmp/
scp -o StrictHostKeyChecking=no -i "%KEY_PATH%" "%~dp0deploy.tgz" %USER%@%SERVER_IP%:/home/bitnami/
if %errorlevel% neq 0 (
    echo [ERROR] Upload failed. Check scp/ssh PATH or network connectivity.
    pause
    exit /b 1
)

echo [4/6] Configuring Infrastructure ^& [5/6] Verifying Connectivity...
REM 서버 스크립트 실행 (CRLF 제거 및 실행 권한 부여)
ssh -o StrictHostKeyChecking=no -i "%KEY_PATH%" %USER%@%SERVER_IP% "sed -i 's/\x0D$//' /tmp/setup_dns.sh && chmod +x /tmp/setup_dns.sh && sudo bash /tmp/setup_dns.sh"
if %errorlevel% neq 0 (
    echo [ERROR] Remote DNS setup or verification failed.
    pause
    exit /b 1
)

echo [6/6] Building and Launching Docker Containers...
ssh -o StrictHostKeyChecking=no -i "%KEY_PATH%" %USER%@%SERVER_IP% "sudo bash -c 'rm -rf %REMOTE_DIR% && mkdir -p %REMOTE_DIR% && tar -xzf /home/bitnami/deploy.tgz -C %REMOTE_DIR% && rm /home/bitnami/deploy.tgz; cd %REMOTE_DIR% && (docker compose down --remove-orphans || docker-compose down --remove-orphans || true) && (docker compose build --pull || docker-compose build --pull) && (docker compose up -d || docker-compose up -d)'"
if %errorlevel% neq 0 (
    echo [ERROR] Docker deployment failed.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo    🎉 ULTRA FAST DEPLOY SUCCESS! 🎉
echo    URL: http://%SERVER_IP%:8501
echo ======================================================
pause
endlocal
