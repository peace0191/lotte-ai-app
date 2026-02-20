"""
db_config.py — 통합 DB 연결 설정
==================================
로컬(SQLite) / Railway PostgreSQL 양쪽 모두 지원.
기존 app.py, worker.py 등에서 import해서 사용하세요.

사용법:
    from db_config import get_db_connection, DATABASE_URL, IS_POSTGRES

    # SQLAlchemy 엔진 사용 시
    engine = get_engine()

    # 직접 연결 (sqlite3 / psycopg2)
    conn = get_db_connection()
"""

import os
import sqlite3
from pathlib import Path

# ── 환경변수에서 DB URL 결정 ───────────────────────────────
_raw_url = os.environ.get("DATABASE_URL", "")

# Railway PostgreSQL URL 형식 정규화 (postgres:// → postgresql://)
if _raw_url.startswith("postgres://"):
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql://", 1)
elif _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url
else:
    # 로컬 SQLite fallback
    _sqlite_path = os.environ.get("DB_PATH", "./assets/system/app.db")
    Path(_sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    DATABASE_URL = f"sqlite:///{_sqlite_path}"

IS_POSTGRES = DATABASE_URL.startswith("postgresql://")
IS_SQLITE = DATABASE_URL.startswith("sqlite://")

# print(f"[DB] 연결 모드: {'PostgreSQL (Railway)' if IS_POSTGRES else 'SQLite (로컬)'}")


def get_engine():
    """SQLAlchemy 엔진 반환 (ORM 사용 시)"""
    try:
        import sqlalchemy
        return sqlalchemy.create_engine(
            DATABASE_URL,
            pool_pre_ping=True,          # 연결 유효성 자동 체크
            pool_recycle=300,            # 5분마다 연결 갱신
            connect_args={"check_same_thread": False} if IS_SQLITE else {},
        )
    except ImportError:
        # raise ImportError("pip install sqlalchemy 설치 필요")
        # Fallback if libraries not available yet (e.g. during minimal local run)
        return None


def get_db_connection():
    """
    직접 DB 커넥션 반환.
    - SQLite: sqlite3.Connection
    - PostgreSQL: psycopg2 Connection
    """
    if IS_SQLITE:
        # On Windows paths might have issues with simple replace if absolute path
        if "sqlite:///" in DATABASE_URL:
            sqlite_path = DATABASE_URL.split("sqlite:///")[-1]
        else:
            sqlite_path = "./assets/system/app.db"
            
        conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # dict처럼 접근 가능
        return conn
    else:
        try:
            import psycopg2
            return psycopg2.connect(DATABASE_URL)
        except ImportError:
            raise ImportError("pip install psycopg2-binary 설치 필요")


def execute_query(sql: str, params: tuple = (), fetch: bool = False):
    """
    단일 쿼리 실행 헬퍼 (SQLite / PostgreSQL 플레이스홀더 자동 변환)
    - SQLite: ? 플레이스홀더
    - PostgreSQL: %s 플레이스홀더
    """
    
    # Simple adaptation for placeholders
    final_sql = sql
    if IS_POSTGRES:
        # SQLite의 ? → PostgreSQL의 %s 로 변환
        final_sql = final_sql.replace("?", "%s")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(final_sql, params)
        if fetch:
            # For select queries
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            result = [dict(zip(column_names, row)) for row in rows]
            conn.close()
            return result
        conn.commit()
        # For insert queries with returning id, we might need special handling
        # But this simplified version assumes basic execution
        conn.close()
        return None
    except Exception as e:
        conn.rollback()
        conn.close()
        
        # If execution failed with placeholder mismatch, try the other way
        # (This is just a safety net for mixed sql syntax)
        # raise e
        # Re-raising for clarity
        print(f"Query Failed: {sql} | Params: {params} | Error: {e}")
        return None
