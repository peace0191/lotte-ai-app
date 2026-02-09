from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

# 상태 관리를 위한 Enum
class ReservationStatus(str, enum.Enum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"

class DealStatus(str, enum.Enum):
    NEGOTIATING = "negotiating"
    SIGNED = "signed"
    FAILED = "failed"

# 1. Demand (수요자)
class Demand(Base):
    __tablename__ = "demand_profile"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    name = Column(String)
    budget_deposit = Column(Float)  # 보증금/전세금
    budget_monthly = Column(Float)  # 월세
    area_min = Column(Integer)
    area_max = Column(Integer)
    move_in_date = Column(Date, nullable=True)
    preferred_regions = Column(String)  # "대치,잠실"
    preferences = Column(JSON, default={}) # {"school": "대치초", "subway": "3호선"}
    created_at = Column(DateTime, default=datetime.utcnow)

# 2. Supply (공급자/매물)
class Supply(Base):
    __tablename__ = "supply_listing"

    id = Column(Integer, primary_key=True, index=True)
    complex_name = Column(String) # 아파트명
    address = Column(String)
    region = Column(String)
    area_py = Column(Integer)
    floor = Column(Integer)
    deal_type = Column(String)  # "매매/전세/월세"
    price = Column(Float)       # 매매가/보증금
    monthly = Column(Float)     # 월세
    available_from = Column(Date, nullable=True)
    features = Column(JSON, default={}) # {"room": 3, "bath": 2, "special": "olive_remodel"}
    risk_flags = Column(JSON, default={}) 
    passcode = Column(String, nullable=True) # 중개사/집주인 확인용 비번
    created_at = Column(DateTime, default=datetime.utcnow)

# 3. Match Candidate (AI 매칭 기록)
class MatchCandidate(Base):
    __tablename__ = "match_candidate"

    id = Column(Integer, primary_key=True, index=True)
    demand_id = Column(Integer, ForeignKey("demand_profile.id"))
    listing_id = Column(Integer, ForeignKey("supply_listing.id"))
    score = Column(Float) # 0.0 ~ 100.0
    reason = Column(JSON) # {"upside": "학군지", "risk": "전세가율"}
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# 4. Reservation (예약)
class Reservation(Base):
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, index=True)
    demand_id = Column(Integer, ForeignKey("demand_profile.id"))
    listing_id = Column(Integer, ForeignKey("supply_listing.id"))
    status = Column(String, default=ReservationStatus.PROPOSED)
    visit_at = Column(DateTime)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# 5. Deal (계약 - 매출 발생)
class Deal(Base):
    __tablename__ = "deal"

    id = Column(Integer, primary_key=True, index=True)
    demand_id = Column(Integer, ForeignKey("demand_profile.id"))
    listing_id = Column(Integer, ForeignKey("supply_listing.id"))
    reservation_id = Column(Integer, ForeignKey("reservation.id"), nullable=True)
    status = Column(String, default=DealStatus.NEGOTIATING)
    signed_at = Column(DateTime, nullable=True)
    contract_file_url = Column(String, nullable=True) # 전자계약서 링크
    commission = Column(Float, default=0.0) # 중개수수료 (예상)
    created_at = Column(DateTime, default=datetime.utcnow)

# 6. Event Log (학습용 로그)
class EventLog(Base):
    __tablename__ = "event_log"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)  
    # view, search, match_click, reservation_req, reservation_confirm, deal_success
    user_id = Column(String, nullable=True) # 세션 ID 등
    meta = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
