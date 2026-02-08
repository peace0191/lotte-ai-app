import sqlite3
import os
from datetime import datetime

class DatabaseService:
    def __init__(self, db_path=None):
        if db_path is None:
            # Pathlib을 사용하여 경로를 더 견고하게 잡음
            from pathlib import Path
            base_dir = Path(__file__).resolve().parents[1]
            self.db_path = str(base_dir / "data" / "market_data.db")
        else:
            self.db_path = os.path.abspath(db_path)
            
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        
        # PRAGMA 설정으로 성능 및 무결성 강화
        conn.execute("PRAGMA foreign_keys = ON")
        
        cursor = conn.cursor()
        
        # 1. Complex Master
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complex_master (
                complex_id TEXT PRIMARY KEY,
                complex_name TEXT NOT NULL,
                dong TEXT,
                district TEXT,
                city TEXT
            )
        """)
        
        # 2. Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complex_id TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                area_sqm REAL NOT NULL,
                floor INTEGER,
                price_won INTEGER NOT NULL,
                FOREIGN KEY (complex_id) REFERENCES complex_master(complex_id)
            )
        """)
        
        # 3. Realtime Stats (Stats Cache)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rt_stats (
                complex_id TEXT NOT NULL,
                area_bucket TEXT NOT NULL,
                window_days INTEGER NOT NULL,
                median_won INTEGER NOT NULL,
                count INTEGER NOT NULL,
                iqr_won INTEGER NOT NULL,
                last_updated TEXT NOT NULL,
                PRIMARY KEY (complex_id, area_bucket, window_days),
                FOREIGN KEY (complex_id) REFERENCES complex_master(complex_id)
            )
        """)

        # 4. Ingested Files Tracking (v4.30 Accurate Mode)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingested_files (
                sha256 TEXT PRIMARY KEY,
                file_path TEXT,
                ingested_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

db_svc = DatabaseService()
