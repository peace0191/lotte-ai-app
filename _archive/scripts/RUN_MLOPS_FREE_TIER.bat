@echo off
REM 무료 MLOps 파이프라인 (FastAPI + Airflow) 실행 스크립트
REM Docker가 설치되어 있어야 합니다.

echo ========================================================
echo * [FREE TIER] MLOps AI Platform Starting...
echo * Components: FastAPI (8000), Streamlit (8502), Airflow (8080)
echo ========================================================

REM 1. 데이터베이스 디렉토리 준비
if not exist "mlops\dags" mkdir "mlops\dags"
if not exist "mlops\logs" mkdir "mlops\logs"

REM 2. Airflow DAG 파일 복사 (데모용)
copy mlops_pipeline_code.py mlops\dags\real_estate_pipeline.py > nul

REM 3. Docker Compose 실행
docker-compose -f docker-compose-mlops.yml up -d --build

echo.
echo ========================================================
echo * [SUCCESS] Platform is Running!
echo * 1. API Server  : http://localhost:8000/docs
echo * 2. Airflow UI  : http://localhost:8080 (ID: admin / PW: admin)
echo * 3. App Frontend: http://localhost:8502
echo ========================================================
pause
