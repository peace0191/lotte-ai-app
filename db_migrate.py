"""
db_migrate.py — SQLite → PostgreSQL 마이그레이션 헬퍼
=====================================================
Railway에서 PostgreSQL 플러그인 추가 시 사용.

사용법:
    python db_migrate.py

Railway Variables에 DATABASE_URL이 세팅된 상태에서 실행하면
기존 SQLite 데이터를 PostgreSQL로 복사합니다.
"""

import os
import sqlite3
import sys

# ── 환경변수에서 DB URL 읽기 ───────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")
SQLITE_PATH = os.environ.get("DB_PATH", "./assets/system/app.db") # Adjusted path to match project structure


def get_pg_engine():
    """PostgreSQL 연결 엔진 반환"""
    try:
        import sqlalchemy
        url = DATABASE_URL
        # Railway는 postgres:// 형식으로 주는 경우가 있음
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return sqlalchemy.create_engine(url)
    except ImportError:
        print("❌ sqlalchemy 설치 필요: pip install sqlalchemy psycopg2-binary")
        sys.exit(1)


def get_sqlite_tables(sqlite_path: str) -> list[str]:
    """SQLite에서 테이블 목록 반환"""
    if not os.path.exists(sqlite_path):
        return []
        
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def migrate_table(table: str, sqlite_path: str, pg_engine):
    """테이블 단위 마이그레이션"""
    import pandas as pd

    print(f"  📋 테이블 마이그레이션 중: {table}")
    conn = sqlite3.connect(sqlite_path)
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        df.to_sql(table, pg_engine, if_exists="replace", index=False)
        print(f"  ✅ {table}: {len(df)}행 완료")
    except Exception as e:
        print(f"  ⚠️  {table} 실패: {e}")
    finally:
        conn.close()


def main():
    print("=" * 50)
    print("🔄 SQLite → PostgreSQL 마이그레이션 시작")
    print("=" * 50)

    # 사전 체크
    if not DATABASE_URL:
        print("❌ DATABASE_URL 환경변수가 없습니다.")
        print("   Railway Dashboard > Variables에서 PostgreSQL 플러그인을 추가하세요.")
        sys.exit(1)

    if not os.path.exists(SQLITE_PATH):
        print(f"❌ SQLite DB 파일 없음: {SQLITE_PATH}")
        print("   로컬 데이터가 없으므로 마이그레이션을 건너뜁니다.")
        return

    try:
        import pandas  # noqa
    except ImportError:
        print("❌ pandas 설치 필요: pip install pandas")
        sys.exit(1)

    # 마이그레이션 실행
    pg_engine = get_pg_engine()
    tables = get_sqlite_tables(SQLITE_PATH)
    
    # Filter out sqlite system tables just in case
    tables = [t for t in tables if not t.startswith('sqlite_')]

    print(f"\n📂 SQLite 경로: {SQLITE_PATH}")
    print(f"🗄️  이전할 테이블 수: {len(tables)}개")
    print(f"   → {', '.join(tables)}\n")

    for table in tables:
        migrate_table(table, SQLITE_PATH, pg_engine)

    print("\n🎉 마이그레이션 완료!")
    print("=" * 50)


if __name__ == "__main__":
    main()
