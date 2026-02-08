@echo off
chcp 65001 >nul
echo.
echo ========================================================
echo  [SYSTEM] 대치1동 AI 부동산 앱을 실행합니다...
echo  (기존 실행중인 화면을 정리하고 새롭게 시작합니다)
echo ========================================================
echo.

:: 1. 기존 파이썬 프로세스 종료 (충돌 방지)
taskkill /F /IM python.exe /T >nul 2>&1

:: 2. 캐시 파일 삭제 (최신 코드 반영 강제)
if exist "__pycache__" rd /s /q "__pycache__"
if exist "services\__pycache__" rd /s /q "services\__pycache__"
if exist "pages\__pycache__" rd /s /q "pages\__pycache__"

:: 3. 프로젝트 폴더로 이동 및 실행
cd /d "c:\Users\PEACE\5차_AI\Lotte_AI_Browser_RunBAT_Demo\LotteTower_AI_SalesApp_Python"
call run_windows.bat
