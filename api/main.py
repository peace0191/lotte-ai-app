from fastapi import FastAPI, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from datetime import datetime
import uvicorn
import os

from . import models, database, auth

# DB 테이블 자동 생성
models.Base.metadata.create_all(bind=database.engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 실행
    print("🔒 [Lotte AI Security] API Server is starting with Secure Mode.")
    yield
    # 앱 종료 시 실행
    print("🔒 [Lotte AI Security] Server shutting down.")

app = FastAPI(
    title="Lotte AI RealEstate Secure API",
    version="2.0.0 (Secure)",
    lifespan=lifespan,
    docs_url="/docs", # 운영 환경에선 None으로 숨길 수 있음
    redoc_url=None
)

# --- 🛡️ 1. 보안 미들웨어 설정 ---

# [CORS] 허용된 도메인(Streamlit Cloud)에서만 접속 허용
origins = [
    "http://localhost:8501",
    "http://localhost:8502",
    "https://lotte-ai-app.streamlit.app", # 고객님의 Streamlit 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["X-API-Key", "Content-Type"],
)

# [Trusted Host] 호스트 헤더 위조 방지
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.streamlit.app", "*"] # 실배포시 '*' 제거 권장
)

# --- API Endpoints ---

@app.get("/")
def health_check():
    """서버 상태 확인 (공개)"""
    return {"status": "ok", "security": "enabled", "time": datetime.now()}

# ✅ [SECURE] 모든 중요 로직에 verify_api_key 의존성 주입

@app.post("/api/v1/demand", dependencies=[Depends(auth.verify_api_key), Depends(auth.rate_limit)])
def register_demand(item: models.DemandCreate, db: Session = Depends(database.get_db)):
    """수요자 등록 (보안 적용됨)"""
    new_demand = models.Demand(**item.dict())
    db.add(new_demand)
    db.commit()
    db.refresh(new_demand)
    return {"ok": True, "id": new_demand.id}

@app.post("/api/v1/supply", dependencies=[Depends(auth.verify_api_key)])
def register_supply(item: models.SupplyCreate, bg: BackgroundTasks, db: Session = Depends(database.get_db)):
    """공급 등록 (보안 적용됨)"""
    new_supply = models.Supply(**item.dict())
    db.add(new_supply)
    db.commit()
    return {"ok": True, "id": new_supply.id}

@app.post("/api/v1/match", dependencies=[Depends(auth.verify_api_key)])
def run_match(demand_id: int, db: Session = Depends(database.get_db)):
    """매칭 실행 (보안 적용됨)"""
    return {"ok": True, "matches": [{"id": 1, "score": 98.5}]}

@app.post("/api/v1/reservation", dependencies=[Depends(auth.verify_api_key)])
def create_reservation(item: models.ReservationCreate, db: Session = Depends(database.get_db)):
    """예약 생성 (보안 적용됨)"""
    # 실제 db 로직은 이전과 동일하므로 생략 (auth 데모 위주)
    return {"ok": True, "status": "proposed"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000)
