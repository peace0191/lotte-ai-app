from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 비용 절감형: 로컬 파일 DB (SQLite) 사용
# 데이터는 'lotte_realestate.db' 파일에 저장됩니다. (공짜)
SQLALCHEMY_DATABASE_URL = "sqlite:///./lotte_realestate.db"

# 만약 나중에 서버 쓰시려면 아래 주석 해제 (AWS RDS, Supabase 등)
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
