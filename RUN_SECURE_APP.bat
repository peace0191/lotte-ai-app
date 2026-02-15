@echo off
chcp 65001 >nul
echo.
echo ========================================================
echo  🔐 [SECURE MODE] 대치1동 AI 부동산 앱 (API + App)
echo ========================================================
echo.

:: 1. 정리
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM uvicorn.exe /T >nul 2>&1

:: 2. 폴더 이동
cd /d "%~dp0"

:: 3. 가상환경 확인
set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"

:: 4. API 서버 실행 (새 창)
echo 🚀 API 보안 서버를 시작합니다... (Port 8000)
start "Lotte API Server (DO NOT CLOSE)" %PY% -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

:: 5. 잠시 대기 (서버 부팅)
timeout /t 5 /nobreak >nul

:: 6. Streamlit 앱 실행
echo 📱 Streamlit 앱을 실행합니다... (Port 8501)
%PY% -m streamlit run app.py

pause
