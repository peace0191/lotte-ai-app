from fastapi import FastAPI, Depends, BackgroundTasks, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from datetime import datetime, date
import uvicorn
import os
import json

# Import internal modules (relative imports for package structure)
from . import models, database, auth, schemas

# Initialize DB tables
models.Base.metadata.create_all(bind=database.engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔒 [Lotte AI Security] API Server is starting with Secure Mode.")
    yield
    print("🔒 [Lotte AI Security] Server shutting down.")

app = FastAPI(
    title="Lotte AI RealEstate Secure API",
    version="2.1.0 (VIP Survey)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None
)

# --- 1. Security Middleware ---
origins = [
    "http://localhost:8501",
    "http://localhost:8502",
    "https://lotte-ai-app.streamlit.app",
    "https://share.streamlit.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"], # Allow all headers including X-API-Key
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.streamlit.app", "*"]
)

# --- 2. Endpoints ---

@app.get("/")
def health_check():
    return {"status": "ok", "security": "enabled", "time": datetime.now()}

# --- VIP Survey Endpoint ---
@app.post("/api/v1/vip-survey", dependencies=[Depends(auth.verify_api_key), Depends(auth.rate_limit)])
def register_vip_survey(item: schemas.VipSurveyInput, db: Session = Depends(database.get_db)):
    """
    VIP 50문항 설문 제출 처리
    - Demand 테이블에 저장 (preferences JSON 컬럼 활용)
    """
    # 1. Extract core fields from survey_data if possible
    # This is optional parsing logic to populate SQL columns for faster query later
    survey = item.survey_data
    
    # Try to parse budget (Q28: "15억" -> 1.5e9)
    budget_deposit = 0.0
    try:
        q28 = survey.get("q28", "0")
        if "억" in str(q28):
            val = float(str(q28).replace("억", "").replace(",", "").strip())
            budget_deposit = val * 100000000
    except:
        pass

    # Try to parse move_in_date (Q46: "2024-03-01")
    move_in_date = None
    try:
        q46 = survey.get("q46")
        if q46:
            move_in_date = datetime.strptime(str(q46), "%Y-%m-%d").date()
    except:
        pass

    # 2. Create Demand Record
    new_demand = models.Demand(
        name=item.user_name,
        phone=item.user_phone,
        budget_deposit=budget_deposit,
        move_in_date=move_in_date,
        preferences=survey, # Store full JSON
        created_at=datetime.utcnow()
    )
    
    db.add(new_demand)
    db.commit()
    db.refresh(new_demand)
    
    return {
        "ok": True, 
        "id": new_demand.id, 
        "message": "VIP 설문이 안전하게 저장되었습니다."
    }

# --- Existing Endpoints (Updated with correct Schemas) ---

@app.post("/api/v1/demand", dependencies=[Depends(auth.verify_api_key)])
def register_demand(item: schemas.DemandCreate, db: Session = Depends(database.get_db)):
    new_demand = models.Demand(**item.dict())
    db.add(new_demand)
    db.commit()
    db.refresh(new_demand)
    return {"ok": True, "id": new_demand.id}

@app.post("/api/v1/supply", dependencies=[Depends(auth.verify_api_key)])
def register_supply(item: schemas.SupplyCreate, bg: BackgroundTasks, db: Session = Depends(database.get_db)):
    new_supply = models.Supply(**item.dict())
    db.add(new_supply)
    db.commit()
    db.refresh(new_supply)
    return {"ok": True, "id": new_supply.id}

@app.post("/api/v1/match", dependencies=[Depends(auth.verify_api_key)])
def run_match(demand_id: int, db: Session = Depends(database.get_db)):
    # Placeholder matching logic
    return {"ok": True, "matches": [{"id": 1, "score": 98.5}]}

@app.post("/api/v1/reservation", dependencies=[Depends(auth.verify_api_key)])
def create_reservation(item: schemas.ReservationCreate, db: Session = Depends(database.get_db)):
    new_res = models.Reservation(**item.dict())
    new_res.status = "proposed"
    db.add(new_res)
    db.commit()
    return {"ok": True, "status": "proposed"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000)
