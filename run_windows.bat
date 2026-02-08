@echo off
setlocal

REM Always run from this BAT folder (project root)
cd /d "%~dp0"

REM Create required folders
if not exist "outputs" mkdir "outputs"
if not exist "outputs\videos" mkdir "outputs\videos"
if not exist "outputs\tts" mkdir "outputs\tts"

REM Choose python (venv first, else system python)
set "PY=%cd%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

REM Install Dependencies (Auto-Fix)
echo Installing dependencies...
echo Installing dependencies... >> app_run.log
%PY% -m pip install -r requirements.txt >> app_run.log 2>&1

REM Start fresh log
echo ===== START ===== > app_run.log
echo BAT_DIR=%~dp0 >> app_run.log
echo CWD=%cd% >> app_run.log
echo PY=%PY% >> app_run.log

REM Diagnose environment
where python >> app_run.log 2>&1
where streamlit >> app_run.log 2>&1
%PY% -c "import sys; print(sys.executable); print(sys.version)" >> app_run.log 2>&1
%PY% -c "import streamlit; print(streamlit.__version__)" >> app_run.log 2>&1

REM Run streamlit
echo ===== RUN STREAMLIT ===== >> app_run.log
%PY% -m streamlit run app.py >> app_run.log 2>&1

REM Show last lines
powershell -NoProfile -Command "Get-Content -Path app_run.log -Tail 120"
pause
