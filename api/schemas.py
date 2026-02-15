from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime

# --- 1. Demand (수요자) Schemas ---
class DemandBase(BaseModel):
    name: str
    phone: str
    budget_deposit: Optional[float] = None  # 보증금/전세금
    budget_monthly: Optional[float] = None  # 월세
    area_min: Optional[int] = None
    area_max: Optional[int] = None
    move_in_date: Optional[date] = None
    preferred_regions: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {} # 설문 데이터 전체 저장

class DemandCreate(DemandBase):
    pass

class Demand(DemandBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True # Pydantic v2 (orm_mode in v1)

# --- 2. Supply (공급자) Schemas ---
class SupplyBase(BaseModel):
    complex_name: str
    address: str
    region: str
    area_py: int
    floor: int
    deal_type: str
    price: float
    monthly: float = 0.0
    available_from: Optional[date] = None
    features: Optional[Dict[str, Any]] = {}
    risk_flags: Optional[Dict[str, Any]] = {}
    passcode: Optional[str] = None

class SupplyCreate(SupplyBase):
    pass

class Supply(SupplyBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- 3. Reservation Schemas ---
class ReservationBase(BaseModel):
    demand_id: int
    listing_id: int
    visit_at: datetime
    message: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- 4. VIP Survey Specific Schema ---
class VipSurveyInput(BaseModel):
    user_name: str
    user_phone: str
    survey_data: Dict[str, Any] # 50문항 답변 전체
