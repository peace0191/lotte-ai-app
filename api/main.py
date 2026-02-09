from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
import uvicorn
import random

from . import models, database

# DB 초기화
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Lotte AI RealEstate Platform API",
    description="Streamlit App과 연동되는 5달러 가성비 API 서버",
    version="1.0.0"
)

# --- 요청 모델 (Pydantic) ---
class DemandIN(BaseModel):
    phone: str
    name: str
    budget_deposit: float
    budget_monthly: float = 0
    area_min: int
    area_max: int
    preferred_regions: str
    preferences: dict = {}

class SupplyIN(BaseModel):
    complex_name: str
    address: str
    region: str
    deal_type: str
    price: float
    area_py: int
    floor: int
    features: dict = {}

class ReservationIN(BaseModel):
    demand_id: int
    listing_id: int
    visit_at: str # ISO Format String
    message: str = ""

# --- 백그라운드 작업 (Airflow 시뮬레이션) ---
def background_shorts_generation(listing_id: int, complex_name: str):
    """
    매물이 등록되면 백그라운드에서 실행되는 로직.
    실제 서비스라면 여기서 Airflow API를 호출하거나, Celery 큐에 작업을 넣습니다.
    """
    print(f"🎬 [AI Shorts] '{complex_name}'(ID:{listing_id}) 영상 생성 시작...")
    import time
    time.sleep(2) # 렌더링 시뮬레이션
    print(f"✅ [AI Shorts] 영상 생성 완료. YouTube 업로드 대기 중.")

# --- API 엔드포인트 ---

@app.get("/")
def health_check():
    return {"status": "ok", "service": "lotte-ai-api", "time": datetime.now()}

# 1. 수요자 등록
@app.post("/api/v1/demand")
def register_demand(item: DemandIN, db: Session = Depends(database.get_db)):
    # 기존 등록 확인 (전화번호 기준)
    existing = db.query(models.Demand).filter(models.Demand.phone == item.phone).first()
    if existing:
        return {"ok": True, "id": existing.id, "msg": "이미 등록된 고객입니다.", "is_new": False}
    
    new_demand = models.Demand(**item.dict())
    db.add(new_demand)
    db.commit()
    db.refresh(new_demand)
    return {"ok": True, "id": new_demand.id, "msg": "수요자 등록 완료", "is_new": True}

# 2. 매물 등록 (공급)
@app.post("/api/v1/supply")
def register_supply(item: SupplyIN, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    new_supply = models.Supply(**item.dict())
    db.add(new_supply)
    db.commit()
    db.refresh(new_supply)
    
    # 숏츠 생성 트리거 (비동기)
    background_tasks.add_task(background_shorts_generation, new_supply.id, new_supply.complex_name)
    
    return {"ok": True, "id": new_supply.id, "msg": "매물 등록 및 마케팅 시작"}

# 3. 매물 리스트 조회 (AI 추천 용)
@app.get("/api/v1/listings")
def get_listings(region: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Supply)
    if region:
        query = query.filter(models.Supply.region.contains(region))
    return query.all()

# 4. AI 매칭 실행
@app.post("/api/v1/match")
def run_matching(demand_id: int, db: Session = Depends(database.get_db)):
    """
    수요자(demand_id)에게 가장 적합한 매물을 찾아 점수를 매겨 반환
    """
    demand = db.query(models.Demand).filter(models.Demand.id == demand_id).first()
    if not demand:
        raise HTTPException(status_code=404, detail="Demand not found")
    
    # 모든 매물 조회 (실제론 vector search 등 사용)
    all_supplies = db.query(models.Supply).all()
    results = []
    
    for s in all_supplies:
        # 간단한 룰 기반 스코어링 (가격, 평수 매칭)
        score = 70.0 # 기본 점수
        
        # 1. 예산 체크
        if s.price <= demand.budget_deposit * 1.1: # 예산 10% 초과까지 허용
            score += 15
        else:
            score -= 20
            
        # 2. 평수 체크
        if demand.area_min <= s.area_py <= demand.area_max:
             score += 15
        
        # 랜덤 노이즈 (AI 느낌)
        score += random.uniform(-2, 5)
        score = min(99.9, max(0.0, score))
        
        results.append({
            "listing_id": s.id,
            "complex_name": s.complex_name,
            "score": round(score, 1),
            "price": s.price,
            "area": s.area_py,
            "reason": "예산 및 평형 적절" if score > 80 else "조건 일부 불일치"
        })
    
    # 점수순 정렬
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"ok": True, "demand_id": demand_id, "matches": results[:10]}

# 5. 예약 신청
@app.post("/api/v1/reservation")
def make_reservation(item: ReservationIN, db: Session = Depends(database.get_db)):
    try:
        visit_dt = datetime.fromisoformat(item.visit_at)
    except ValueError:
        visit_dt = datetime.now() # Fallback
        
    res = models.Reservation(
        demand_id=item.demand_id,
        listing_id=item.listing_id,
        visit_at=visit_dt,
        message=item.message,
        status=models.ReservationStatus.PROPOSED
    )
    db.add(res)
    db.commit()
    db.refresh(res)
    
    # 로그 기록
    log = models.EventLog(event_type="reservation_create", meta={"res_id": res.id})
    db.add(log)
    db.commit()
    
    return {"ok": True, "reservation_id": res.id, "status": "proposed"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
