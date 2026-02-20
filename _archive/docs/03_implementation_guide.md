# 🛠️ 부동산 AI 플랫폼 - 개발팀 구현 가이드

> **목적**: 시스템 아키텍처를 실제 코드로 구현하기 위한 단계별 가이드  
> **대상**: Backend/ML/DevOps 개발자

---

## 📋 목차

1. [개발 환경 설정](#1-개발-환경-설정)
2. [데이터베이스 스키마 설계](#2-데이터베이스-스키마-설계)
3. [데이터 파이프라인 구현](#3-데이터-파이프라인-구현)
4. [ML 모델 개발 가이드](#4-ml-모델-개발-가이드)
5. [API 서버 구현](#5-api-서버-구현)
6. [MLflow 설정 및 운영](#6-mlflow-설정-및-운영)
7. [배포 및 인프라](#7-배포-및-인프라)
8. [모니터링 및 알림](#8-모니터링-및-알림)
9. [테스트 전략](#9-테스트-전략)
10. [보안 및 규정 준수](#10-보안-및-규정-준수)

---

## 1. 개발 환경 설정

### 1.1 필수 도구 설치

```bash
# Python 3.10 이상
python --version

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt
```

### 1.2 requirements.txt

```text
# ML & Data
pandas==2.1.4
numpy==1.26.2
scikit-learn==1.3.2
xgboost==2.0.3
lightgbm==4.1.0
shap==0.44.0

# MLflow
mlflow==2.9.2
boto3==1.34.10  # S3 연동

# API
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
python-multipart==0.0.6

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.25

# Data Pipeline
apache-airflow==2.8.0
requests==2.31.0
beautifulsoup4==4.12.3

# Monitoring
prometheus-client==0.19.0
sentry-sdk==1.39.2

# Utils
python-dotenv==1.0.0
loguru==0.7.2
```

### 1.3 환경 변수 설정

```bash
# .env 파일
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/realestate_db

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_SECRET_KEY=your-secret-key-here
API_CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# External APIs
MOLIT_API_KEY=your-molit-api-key  # 국토부 API
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret
```

### 1.4 Docker 개발 환경

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: realestate_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data

  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.2
    ports:
      - "5000:5000"
    environment:
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin
    command: >
      mlflow server
      --backend-store-uri postgresql://admin:password123@postgres:5432/mlflow_db
      --default-artifact-root s3://mlflow/
      --host 0.0.0.0

volumes:
  postgres_data:
  minio_data:
```

---

## 2. 데이터베이스 스키마 설계

### 2.1 ERD (Entity Relationship Diagram)

```
┌─────────────────┐       ┌──────────────────┐
│   properties    │       │   transactions   │
├─────────────────┤       ├──────────────────┤
│ id (PK)         │──────<│ property_id (FK) │
│ address         │       │ contract_date    │
│ building_type   │       │ contract_price   │
│ area_sqm        │       │ buyer_id (FK)    │
│ floor           │       └──────────────────┘
│ price           │
│ created_at      │       ┌──────────────────┐
└─────────────────┘       │   user_profiles  │
                          ├──────────────────┤
┌─────────────────┐       │ id (PK)          │
│   features      │       │ age              │
├─────────────────┤       │ income_range     │
│ id (PK)         │       │ preferred_area   │
│ property_id(FK) │<──┐   │ budget_min       │
│ avg_price_3m    │   │   │ budget_max       │
│ price_change_pct│   │   └──────────────────┘
│ subway_distance │   │
│ school_score    │   │   ┌──────────────────┐
│ jeonse_ratio    │   │   │  model_metadata  │
│ updated_at      │   │   ├──────────────────┤
└─────────────────┘   │   │ id (PK)          │
                      │   │ model_name       │
┌─────────────────┐   │   │ model_version    │
│  predictions    │   │   │ stage            │
├─────────────────┤   │   │ metrics          │
│ id (PK)         │   │   │ created_at       │
│ property_id(FK) │───┘   └──────────────────┘
│ model_version   │
│ undervalued_score│      ┌──────────────────┐
│ prediction_date │       │   api_logs       │
│ shap_values     │       ├──────────────────┤
└─────────────────┘       │ id (PK)          │
                          │ endpoint         │
                          │ request_data     │
                          │ response_data    │
                          │ latency_ms       │
                          │ timestamp        │
                          └──────────────────┘
```

### 2.2 SQL 스키마 정의

```sql
-- properties 테이블
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    building_type VARCHAR(50),  -- '아파트', '오피스텔', '빌라'
    area_sqm DECIMAL(10, 2),
    floor INTEGER,
    price BIGINT,  -- 매매가 (만원)
    jeonse_price BIGINT,  -- 전세가 (만원)
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    listing_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_properties_location ON properties(latitude, longitude);
CREATE INDEX idx_properties_price ON properties(price);
CREATE INDEX idx_properties_listing_date ON properties(listing_date);

-- features 테이블 (ML 피처)
CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    avg_price_3m BIGINT,  -- 최근 3개월 평균 거래가
    price_change_pct DECIMAL(5, 2),  -- 가격 변동률
    subway_distance_m INTEGER,  -- 지하철역 거리
    school_score DECIMAL(3, 1),  -- 학군 점수 (1-10)
    jeonse_ratio DECIMAL(5, 2),  -- 전세가율
    crime_rate DECIMAL(5, 2),  -- 범죄율
    population_density INTEGER,  -- 인구밀도
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- transactions 테이블 (실거래 이력)
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    contract_date DATE NOT NULL,
    contract_price BIGINT NOT NULL,
    buyer_id INTEGER REFERENCES user_profiles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_date ON transactions(contract_date);

-- user_profiles 테이블
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER,
    income_range VARCHAR(50),
    preferred_area VARCHAR(100),
    budget_min BIGINT,
    budget_max BIGINT,
    family_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- predictions 테이블 (모델 예측 결과)
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    undervalued_score DECIMAL(5, 2),  -- 저평가 점수 (0-100)
    predicted_price BIGINT,
    shap_values JSONB,  -- SHAP 설명
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_property ON predictions(property_id);
CREATE INDEX idx_predictions_score ON predictions(undervalued_score DESC);

-- model_metadata 테이블 (MLflow Registry 동기화)
CREATE TABLE model_metadata (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    stage VARCHAR(20),  -- 'Production', 'Staging', 'Archived'
    metrics JSONB,  -- {'mae': 300, 'rmse': 500, ...}
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_name, model_version)
);

-- api_logs 테이블 (API 호출 로그)
CREATE TABLE api_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    request_data JSONB,
    response_data JSONB,
    status_code INTEGER,
    latency_ms INTEGER,
    user_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_logs_timestamp ON api_logs(timestamp);
CREATE INDEX idx_api_logs_endpoint ON api_logs(endpoint);
```

---

## 3. 데이터 파이프라인 구현

### 3.1 Airflow DAG 구조

```python
# dags/property_data_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'property_data_pipeline',
    default_args=default_args,
    description='부동산 데이터 수집 및 전처리',
    schedule_interval='0 2 * * *',  # 매일 새벽 2시
    start_date=days_ago(1),
    catchup=False,
    tags=['data', 'etl'],
)

# Task 1: 공공 API 수집
collect_public_data = PythonOperator(
    task_id='collect_public_data',
    python_callable=collect_molit_data,
    dag=dag,
)

# Task 2: 크롤링
crawl_property_sites = PythonOperator(
    task_id='crawl_property_sites',
    python_callable=crawl_naver_realestate,
    dag=dag,
)

# Task 3: 데이터 검증
validate_data = PythonOperator(
    task_id='validate_data',
    python_callable=validate_collected_data,
    dag=dag,
)

# Task 4: 전처리 및 Feature 생성
feature_engineering = PythonOperator(
    task_id='feature_engineering',
    python_callable=generate_features,
    dag=dag,
)

# Task 5: DB 적재
load_to_db = PythonOperator(
    task_id='load_to_db',
    python_callable=load_data_to_postgres,
    dag=dag,
)

# Task 의존성 설정
[collect_public_data, crawl_property_sites] >> validate_data >> feature_engineering >> load_to_db
```

### 3.2 데이터 수집 함수

```python
# utils/data_collectors.py
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def collect_molit_data(start_date, end_date):
    """국토부 실거래가 API 데이터 수집"""
    API_KEY = os.getenv('MOLIT_API_KEY')
    BASE_URL = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'
    
    results = []
    current_date = start_date
    
    while current_date <= end_date:
        params = {
            'serviceKey': API_KEY,
            'LAWD_CD': '11110',  # 서울 종로구 (예시)
            'DEAL_YMD': current_date.strftime('%Y%m'),
        }
        
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            # XML 파싱 및 데이터 추출
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                results.append({
                    'address': item.find('법정동').text + ' ' + item.find('아파트').text,
                    'area_sqm': float(item.find('전용면적').text),
                    'floor': int(item.find('층').text),
                    'price': int(item.find('거래금액').text.replace(',', '')) * 10000,  # 만원 → 원
                    'contract_date': item.find('년').text + '-' + item.find('월').text + '-' + item.find('일').text,
                })
        
        current_date += timedelta(days=30)
    
    return pd.DataFrame(results)

def crawl_naver_realestate(region='서울'):
    """네이버 부동산 크롤링"""
    # 실제 구현 시 robots.txt 확인 및 준수
    headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = f'https://land.naver.com/article/articleList.naver?rletTypeCd=A01&tradeTypeCd=A1&location={region}'
    
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 실제 구조에 맞게 수정 필요
    properties = []
    for item in soup.select('.item_inner'):
        properties.append({
            'title': item.select_one('.item_title').text,
            'price': item.select_one('.price').text,
            'area': item.select_one('.item_area').text,
        })
    
    return pd.DataFrame(properties)
```

### 3.3 Feature Engineering

```python
# utils/feature_engineering.py
import pandas as pd
import numpy as np
from geopy.distance import geodesic

def generate_features(properties_df, transactions_df):
    """ML 모델용 피처 생성"""
    
    features_df = properties_df.copy()
    
    # 1. 시계열 피처
    features_df['avg_price_3m'] = calculate_rolling_avg(transactions_df, window=90)
    features_df['price_change_pct'] = calculate_price_change(transactions_df)
    
    # 2. 지리적 피처
    features_df['subway_distance_m'] = features_df.apply(
        lambda row: nearest_subway_distance(row['latitude'], row['longitude']), 
        axis=1
    )
    
    # 3. 전세가율
    features_df['jeonse_ratio'] = (features_df['jeonse_price'] / features_df['price']) * 100
    
    # 4. 평당 가격
    features_df['price_per_pyeong'] = features_df['price'] / (features_df['area_sqm'] * 0.3025)
    
    # 5. 층 보정 (1층, 최상층 페널티)
    features_df['floor_penalty'] = features_df['floor'].apply(floor_penalty_score)
    
    return features_df

def nearest_subway_distance(lat, lon):
    """가장 가까운 지하철역 거리 계산"""
    # 지하철역 좌표 DB (미리 준비)
    SUBWAY_STATIONS = [
        (37.5665, 126.9780),  # 서울역
        (37.5547, 126.9707),  # 강남역
        # ... 더 많은 역
    ]
    
    property_loc = (lat, lon)
    distances = [geodesic(property_loc, station).meters for station in SUBWAY_STATIONS]
    return min(distances)

def floor_penalty_score(floor):
    """층별 선호도 점수"""
    if floor == 1:
        return -0.05  # -5% 페널티
    elif floor >= 15:
        return -0.03  # -3% 페널티
    elif 5 <= floor <= 10:
        return 0.03  # +3% 프리미엄
    else:
        return 0
```

---

## 4. ML 모델 개발 가이드

### 4.1 저평가 점수 모델 구조

```python
# models/undervalued_model.py
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import shap

class UndervaluedScoreModel:
    def __init__(self, experiment_name='undervalued-score'):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        self.model = None
        
    def train(self, X, y, params=None):
        """모델 학습 및 MLflow 로깅"""
        
        if params is None:
            params = {
                'n_estimators': 200,
                'learning_rate': 0.05,
                'max_depth': 5,
                'min_samples_split': 20,
                'random_state': 42
            }
        
        # Train/Test 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # MLflow Run 시작
        with mlflow.start_run(run_name=f"gb_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            
            # 파라미터 로깅
            mlflow.log_params(params)
            
            # 모델 학습
            self.model = GradientBoostingRegressor(**params)
            self.model.fit(X_train, y_train)
            
            # 예측
            y_pred = self.model.predict(X_test)
            
            # 메트릭 계산
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            # 메트릭 로깅
            mlflow.log_metrics({
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'mae_millions': mae / 10000,  # 만원 단위로 변환
            })
            
            # Feature Importance 로깅
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            mlflow.log_dict(feature_importance.to_dict(), 'feature_importance.json')
            
            # SHAP 값 계산 (설명 가능성)
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_test[:100])  # 샘플 100개
            
            # SHAP plot 저장
            shap.summary_plot(shap_values, X_test[:100], show=False)
            mlflow.log_figure(plt.gcf(), 'shap_summary.png')
            plt.close()
            
            # 모델 저장
            mlflow.sklearn.log_model(
                self.model, 
                'model',
                registered_model_name='undervalued-score-model'
            )
            
            print(f"✅ Model trained: MAE={mae/10000:.0f}만원, RMSE={rmse/10000:.0f}만원, R²={r2:.3f}")
            
            return {
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'run_id': mlflow.active_run().info.run_id
            }
    
    def calculate_undervalued_score(self, property_features):
        """저평가 점수 계산"""
        predicted_price = self.model.predict(property_features)[0]
        actual_price = property_features['price'].values[0]
        
        # 저평가율 계산
        undervalued_pct = ((predicted_price - actual_price) / predicted_price) * 100
        
        # 0-100 점수로 변환
        score = min(max(undervalued_pct * 2, 0), 100)
        
        return {
            'score': score,
            'predicted_price': predicted_price,
            'actual_price': actual_price,
            'undervalued_amount': predicted_price - actual_price
        }
```

### 4.2 모델 학습 스크립트

```python
# scripts/train_undervalued_model.py
import pandas as pd
from models.undervalued_model import UndervaluedScoreModel
from utils.data_loaders import load_training_data

def main():
    # 1. 데이터 로드
    print("📊 Loading training data...")
    X, y = load_training_data()
    
    # 2. 모델 초기화
    model = UndervaluedScoreModel(experiment_name='undervalued-score-v1')
    
    # 3. 하이퍼파라미터 그리드
    param_grid = [
        {'n_estimators': 100, 'learning_rate': 0.1, 'max_depth': 3},
        {'n_estimators': 200, 'learning_rate': 0.05, 'max_depth': 5},
        {'n_estimators': 300, 'learning_rate': 0.03, 'max_depth': 7},
    ]
    
    # 4. 여러 실험 실행
    best_score = float('inf')
    best_run = None
    
    for params in param_grid:
        print(f"\n🔬 Training with params: {params}")
        results = model.train(X, y, params)
        
        if results['mae'] < best_score:
            best_score = results['mae']
            best_run = results['run_id']
    
    print(f"\n✅ Best model: Run {best_run}, MAE={best_score/10000:.0f}만원")
    
    # 5. Registry에 등록
    client = mlflow.tracking.MlflowClient()
    model_uri = f"runs:/{best_run}/model"
    
    # Staging으로 등록
    result = client.create_model_version(
        name="undervalued-score-model",
        source=model_uri,
        run_id=best_run
    )
    
    print(f"📦 Model registered: version {result.version}")

if __name__ == '__main__':
    main()
```

---

## 5. API 서버 구현

### 5.1 FastAPI 애플리케이션 구조

```
api/
├── main.py
├── models/
│   ├── schemas.py
│   └── ml_models.py
├── routers/
│   ├── prediction.py
│   └── health.py
├── dependencies.py
└── config.py
```

### 5.2 API 엔드포인트 구현

```python
# api/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import prediction, health
import mlflow

app = FastAPI(
    title="부동산 AI API",
    description="저평가 매물 발굴 및 매칭 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(prediction.router, prefix="/api/v1", tags=["prediction"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행"""
    # MLflow 모델 로드
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
    print("✅ MLflow connected")

@app.get("/")
async def root():
    return {"message": "부동산 AI API v1.0"}
```

```python
# api/routers/prediction.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import mlflow.pyfunc
from typing import List, Dict
import numpy as np

router = APIRouter()

# Production 모델 로드 (전역)
model = mlflow.pyfunc.load_model("models:/undervalued-score-model/Production")

class PropertyInput(BaseModel):
    address: str
    building_type: str
    area_sqm: float
    floor: int
    price: int
    jeonse_price: int
    latitude: float
    longitude: float

class UndervaluedResponse(BaseModel):
    score: float
    predicted_price: int
    actual_price: int
    undervalued_amount: int
    explanation: Dict[str, float]
    model_version: str

@router.post("/undervalued-score", response_model=UndervaluedResponse)
async def calculate_undervalued_score(property: PropertyInput):
    """
    저평가 점수 계산
    
    - **score**: 0-100 저평가 점수 (높을수록 저평가)
    - **predicted_price**: AI 예측 시세
    - **actual_price**: 실제 매물가
    - **undervalued_amount**: 저평가 금액 (예측-실제)
    - **explanation**: SHAP 기반 판단 근거
    """
    
    try:
        # 피처 생성
        features = generate_features(property)
        
        # 예측
        predicted_price = model.predict(features)[0]
        
        # 저평가 점수 계산
        undervalued_amount = predicted_price - property.price
        undervalued_pct = (undervalued_amount / predicted_price) * 100
        score = min(max(undervalued_pct * 2, 0), 100)
        
        # SHAP 설명 (간단한 버전)
        explanation = {
            'jeonse_ratio': 0.3,  # 실제로는 SHAP 값 계산
            'subway_distance': -0.2,
            'school_score': 0.15,
        }
        
        # API 로그 저장 (비동기 처리)
        log_api_call({
            'endpoint': '/undervalued-score',
            'input': property.dict(),
            'output': {'score': score, 'predicted_price': predicted_price}
        })
        
        return UndervaluedResponse(
            score=round(score, 2),
            predicted_price=int(predicted_price),
            actual_price=property.price,
            undervalued_amount=int(undervalued_amount),
            explanation=explanation,
            model_version='v1.2'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/matching-rank")
async def calculate_matching_rank(
    user_profile: Dict,
    properties: List[PropertyInput]
):
    """
    사용자와 매물 간 매칭 순위 계산
    """
    # 매칭 모델 로드
    matching_model = mlflow.pyfunc.load_model("models:/matching-model/Production")
    
    # 각 매물에 대한 매칭 점수 계산
    results = []
    for prop in properties:
        features = create_matching_features(user_profile, prop)
        match_score = matching_model.predict(features)[0]
        
        results.append({
            'property_id': prop.address,  # 실제로는 ID 사용
            'match_score': float(match_score),
            'property': prop.dict()
        })
    
    # 점수 순으로 정렬
    results = sorted(results, key=lambda x: x['match_score'], reverse=True)
    
    return {'matches': results[:10]}  # 상위 10개 반환
```

### 5.3 캐싱 및 성능 최적화

```python
# api/dependencies.py
from functools import lru_cache
import redis
import json

# Redis 연결
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_prediction(property_key: str):
    """Redis 캐시에서 예측 결과 가져오기"""
    cached = redis_client.get(f"prediction:{property_key}")
    if cached:
        return json.loads(cached)
    return None

def cache_prediction(property_key: str, result: dict, ttl=3600):
    """예측 결과를 Redis에 캐싱 (1시간 TTL)"""
    redis_client.setex(
        f"prediction:{property_key}",
        ttl,
        json.dumps(result)
    )

@lru_cache(maxsize=100)
def get_model(model_name: str, stage: str = "Production"):
    """모델 로딩 캐싱"""
    return mlflow.pyfunc.load_model(f"models:/{model_name}/{stage}")
```

---

## 6. MLflow 설정 및 운영

### 6.1 MLflow 서버 설정

```bash
# MLflow 서버 시작
mlflow server \
  --backend-store-uri postgresql://admin:password@localhost:5432/mlflow_db \
  --default-artifact-root s3://mlflow-artifacts/ \
  --host 0.0.0.0 \
  --port 5000
```

### 6.2 Model Registry 작업 자동화

```python
# scripts/promote_model.py
import mlflow
from mlflow.tracking import MlflowClient

def promote_model_to_production(model_name, version):
    """모델을 Production으로 승격"""
    client = MlflowClient()
    
    # 기존 Production 모델을 Archived로
    current_prod = client.get_latest_versions(model_name, stages=["Production"])
    if current_prod:
        client.transition_model_version_stage(
            name=model_name,
            version=current_prod[0].version,
            stage="Archived"
        )
    
    # 새 모델을 Production으로
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Production"
    )
    
    print(f"✅ Model {model_name} v{version} promoted to Production")

def auto_promote_if_better():
    """성능이 개선되면 자동 승격"""
    client = MlflowClient()
    
    # Staging 모델 가져오기
    staging_models = client.get_latest_versions("undervalued-score-model", stages=["Staging"])
    prod_models = client.get_latest_versions("undervalued-score-model", stages=["Production"])
    
    if not staging_models or not prod_models:
        return
    
    staging_model = staging_models[0]
    prod_model = prod_models[0]
    
    # 메트릭 비교
    staging_run = client.get_run(staging_model.run_id)
    prod_run = client.get_run(prod_model.run_id)
    
    staging_mae = staging_run.data.metrics['mae']
    prod_mae = prod_run.data.metrics['mae']
    
    # 5% 이상 개선되면 승격
    if staging_mae < prod_mae * 0.95:
        promote_model_to_production("undervalued-score-model", staging_model.version)
```

---

## 7. 배포 및 인프라

### 7.1 Kubernetes 배포 설정

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: realestate-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: realestate-api
  template:
    metadata:
      labels:
        app: realestate-api
    spec:
      containers:
      - name: api
        image: realestate-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow-service:5000"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: realestate-api-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: realestate-api
```

### 7.2 CI/CD 파이프라인

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest tests/ --cov=./ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t realestate-api:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push realestate-api:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/realestate-api api=realestate-api:${{ github.sha }}
        kubectl rollout status deployment/realestate-api
```

---

## 8. 모니터링 및 알림

### 8.1 Prometheus 메트릭 수집

```python
# api/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# 메트릭 정의
REQUEST_COUNT = Counter(
    'api_requests_total', 
    'Total API requests',
    ['endpoint', 'method', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_duration_seconds',
    'API request latency',
    ['endpoint']
)

MODEL_PREDICTION_COUNT = Counter(
    'model_predictions_total',
    'Total model predictions',
    ['model_name', 'model_version']
)

ACTIVE_MODELS = Gauge(
    'active_models',
    'Number of active models',
    ['stage']
)

# 미들웨어에서 사용
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        method=request.method,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

### 8.2 Grafana 대시보드 설정

```json
{
  "dashboard": {
    "title": "부동산 AI 모니터링",
    "panels": [
      {
        "title": "API 요청 수",
        "targets": [{
          "expr": "rate(api_requests_total[5m])"
        }]
      },
      {
        "title": "평균 응답 시간",
        "targets": [{
          "expr": "histogram_quantile(0.95, api_request_duration_seconds_bucket)"
        }]
      },
      {
        "title": "모델 예측 수",
        "targets": [{
          "expr": "rate(model_predictions_total[5m])"
        }]
      }
    ]
  }
}
```

---

## 9. 테스트 전략

### 9.1 유닛 테스트

```python
# tests/test_models.py
import pytest
import pandas as pd
from models.undervalued_model import UndervaluedScoreModel

def test_model_prediction():
    """모델 예측 테스트"""
    model = UndervaluedScoreModel()
    
    # 테스트 데이터
    X = pd.DataFrame({
        'area_sqm': [84.5],
        'floor': [10],
        'subway_distance_m': [500],
        'jeonse_ratio': [65.0],
    })
    
    # 예측 (모델이 학습되어 있다고 가정)
    result = model.calculate_undervalued_score(X)
    
    assert 0 <= result['score'] <= 100
    assert result['predicted_price'] > 0

def test_feature_engineering():
    """피처 생성 테스트"""
    from utils.feature_engineering import generate_features
    
    properties_df = pd.DataFrame({
        'price': [50000],
        'jeonse_price': [35000],
        'area_sqm': [84.5],
    })
    
    features = generate_features(properties_df, None)
    
    assert 'jeonse_ratio' in features.columns
    assert features['jeonse_ratio'].iloc[0] == 70.0
```

### 9.2 통합 테스트

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_undervalued_score_endpoint():
    """API 엔드포인트 테스트"""
    payload = {
        "address": "서울시 강남구 역삼동",
        "building_type": "아파트",
        "area_sqm": 84.5,
        "floor": 10,
        "price": 100000,
        "jeonse_price": 70000,
        "latitude": 37.5665,
        "longitude": 126.9780
    }
    
    response = client.post("/api/v1/undervalued-score", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert 'score' in data
    assert 0 <= data['score'] <= 100
```

---

## 10. 보안 및 규정 준수

### 10.1 API 인증

```python
# api/auth.py
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """JWT 토큰 검증"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 엔드포인트에서 사용
@router.post("/undervalued-score")
async def calculate_score(
    property: PropertyInput,
    user = Depends(verify_token)
):
    # ...
```

### 10.2 개인정보 보호

```python
# utils/privacy.py
from cryptography.fernet import Fernet

# 암호화 키 (환경 변수로 관리)
cipher = Fernet(os.getenv('ENCRYPTION_KEY'))

def encrypt_sensitive_data(data: str) -> str:
    """민감 데이터 암호화"""
    return cipher.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted: str) -> str:
    """암호화된 데이터 복호화"""
    return cipher.decrypt(encrypted.encode()).decode()

# 사용 예시
user_phone = encrypt_sensitive_data("010-1234-5678")
```

---

## 마무리

### ✅ 체크리스트

구현 전에 다음 사항을 확인하세요:

- [ ] 개발 환경 설정 완료 (Python, Docker, Postgres)
- [ ] MLflow 서버 실행 확인
- [ ] 데이터베이스 스키마 생성
- [ ] 샘플 데이터 준비
- [ ] 첫 번째 모델 학습 성공
- [ ] API 서버 로컬 실행 확인
- [ ] 테스트 코드 작성 및 통과
- [ ] 모니터링 대시보드 설정

### 📚 추가 학습 자료

- [MLflow 공식 문서](https://mlflow.org/docs/latest/index.html)
- [FastAPI 튜토리얼](https://fastapi.tiangolo.com/tutorial/)
- [Kubernetes 기초](https://kubernetes.io/docs/tutorials/)
- [SHAP 설명 가능 AI](https://shap.readthedocs.io/)

---

**문서 버전**: v1.0  
**최종 수정**: 2026.02.06  
**작성자**: ML Engineering Team
