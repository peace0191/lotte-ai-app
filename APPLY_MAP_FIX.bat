@echo off
chcp 65001 >nul
echo.
echo ========================================================
echo  🗺️ 대치동 지도 좌표 + 라인 완벽 수정 스크립트
echo  정확한 좌표 + 주황/분홍 라인 자동 적용
echo ========================================================
echo.

set "PROJECT_DIR=c:\Users\PEACE\5차_AI\Lotte_AI_Browser_RunBAT_Demo\LotteTower_AI_SalesApp_Python"
set "DATA_DIR=%PROJECT_DIR%\data"
set "PAGES_DIR=%PROJECT_DIR%\pages"
set "BACKUP_DIR=%PROJECT_DIR%\backup"

:: 백업 폴더 생성
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo [1/5] 기존 파일 백업 중...
if exist "%DATA_DIR%\daechi_points.json" (
    copy "%DATA_DIR%\daechi_points.json" "%BACKUP_DIR%\daechi_points_old_%date:~0,4%%date:~5,2%%date:~8,2%.json" >nul
    echo ✅ daechi_points.json 백업 완료
)
if exist "%PAGES_DIR%\dashboard.py" (
    copy "%PAGES_DIR%\dashboard.py" "%BACKUP_DIR%\dashboard_old_%date:~0,4%%date:~5,2%%date:~8,2%.py" >nul
    echo ✅ dashboard.py 백업 완료
)

echo.
echo [2/5] 수정된 데이터 파일 복사 중...
if exist "daechi_points_FINAL.json" (
    if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
    copy /Y "daechi_points_FINAL.json" "%DATA_DIR%\daechi_points.json" >nul
    echo ✅ 정확한 좌표 데이터 적용 완료
) else (
    echo ❌ daechi_points_FINAL.json 파일이 없습니다!
    echo    Claude가 생성한 파일을 먼저 다운로드하세요.
    pause
    exit /b 1
)

echo.
echo [3/5] 수정된 대시보드 파일 복사 중...
if exist "dashboard_FIXED.py" (
    copy /Y "dashboard_FIXED.py" "%PAGES_DIR%\dashboard.py" >nul
    echo ✅ 새로운 라인 (주황+분홍) 적용 완료
) else (
    echo ❌ dashboard_FIXED.py 파일이 없습니다!
    echo    Claude가 생성한 파일을 먼저 다운로드하세요.
    pause
    exit /b 1
)

echo.
echo [4/5] 캐시 파일 정리 중...
if exist "%PROJECT_DIR%\__pycache__" rd /s /q "%PROJECT_DIR%\__pycache__"
if exist "%PAGES_DIR%\__pycache__" rd /s /q "%PAGES_DIR%\__pycache__"
if exist "%PROJECT_DIR%\services\__pycache__" rd /s /q "%PROJECT_DIR%\services\__pycache__"
echo ✅ 캐시 정리 완료

echo.
echo [5/5] Python 프로세스 종료...
taskkill /F /IM python.exe >nul 2>&1
echo ✅ 프로세스 종료 완료

echo.
echo ========================================================
echo  ✅ 모든 수정이 완료되었습니다!
echo.
echo  📍 적용된 내용:
echo     • 정확한 주소/좌표로 업데이트 (12개 위치)
echo     • 기존 빨간 학군 라인 삭제
echo     • 🟠 주황색 라인 추가: 대치초→래미안→SK뷰
echo     • 🩷 분홍색 라인 추가: 단대부중고→아이파크→...→삼환
echo.
echo  이제 [대치1동AI]앱실행_최종.bat 를 실행하세요.
echo.
echo  ⭐ 예상 결과:
echo     - 모든 마커가 실제 주소와 정확히 일치
echo     - 주황색 + 분홍색 2개의 의미 있는 동선 라인
echo     - 각 라인에 화살표(▶) 표시
echo ========================================================
echo.
pause
