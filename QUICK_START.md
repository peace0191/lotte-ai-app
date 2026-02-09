# 🚀 Lotte RealEstate AI Platform - Quick Start Guide

이 가이드는 로컬 개발 환경 설정부터 운영 환경 배포까지의 단계를 안내합니다.

## 1️⃣ 보안 설정 (필수!)

가장 먼저 보안 설정을 완료해야 합니다.

### 1.1 GitHub Private 설정
GitHub 레포지토리 Settings -> Danger Zone -> Change visibility -> **Make private** 선택

### 1.2 .gitignore 확인
다음 파일들이 `.gitignore`에 포함되어 있는지 확인하세요:
- `.streamlit/secrets.toml`
- `.env`
- `*.db`

### 1.3 Secrets 설정 (로컬)
`.streamlit/secrets.toml` 파일을 생성하고 API 키를 설정하세요.
```toml
[api]
url = "http://localhost:8000"
key = "YOUR_SECURE_KEY"
```

## 2️⃣ 로컬 실행 (개발용)

### 2.1 API 서버 실행 (FastAPI)
```bash
# 가상환경 활성화 후
uvicorn api.main:app --reload
```
또는 Docker 사용:
```bash
docker-compose up --build
```

### 2.2 Streamlit 앱 실행
```bash
streamlit run streamlit_app.py
```

## 3️⃣ AWS Lightsail 배포 (운영용)

### 3.1 인스턴스 생성
- AWS Lightsail 콘솔 접속
- **OS Only** -> **Ubuntu 22.04 LTS** 선택
- **$5/month** 플랜 선택
- 인스턴스 이름 설정 후 생성

### 3.2 배포 스크립트 실행
SSH로 접속하여 다음 명령어 실행:
```bash
# 1. 스크립트 다운로드 (또는 git clone 후 실행)
git clone https://github.com/peace0191/lotte-ai-app.git
cd lotte-ai-app
bash deploy/lightsail_setup.sh
```

### 3.3 Streamlit Cloud 연동
Streamlit Cloud -> App Settings -> Secrets에 운영 서버 정보 입력:
```toml
[api]
url = "http://YOUR_LIGHTSAIL_IP:8000"
key = "GENERATED_SECRET_KEY" 
# (배포 스크립트 실행 시 생성된 키 사용)
```

## 4️⃣ 모니터링 및 관리

- **API 문서**: `http://YOUR_IP:8000/docs`
- **로그 확인**: `docker-compose logs -f api`
- **서버 재시작**: `docker-compose restart api`
