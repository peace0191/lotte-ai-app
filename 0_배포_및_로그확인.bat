@echo off
chcp 65001 >nul
title LOTTE AI - ONE CLICK DEPLOY & LOG (v5.2)

echo ======================================================
echo    🚀 롯데 AI 부동산 앱 - 배포 시스템 v5.2 (Excellent)
echo ======================================================
echo.
echo [공지] 기존에 실행 중인 메모장이나 로그 파일을 닫아주세요.
echo.

set LOG_FILE=deploy_log_excellent_v2.txt
if exist "%LOG_FILE%" del /f /q "%LOG_FILE%"

echo [1/2] 배포 스크립트를 실행 중입니다... (로그 저장: %LOG_FILE%)
cmd /c "remote_deploy.bat > %LOG_FILE% 2>&1"

echo.
echo [2/2] 배포 프로세스 종료.
echo.
echo [합격 판정 기준] 아래 2줄이 있으면 Excellent 입니다:
echo 1. [OK] Docker DNS configured.
echo 2. DNS Verification Success: OK
echo.
echo 로그 파일을 엽니다...
start notepad %LOG_FILE%
pause
