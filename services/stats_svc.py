import json
import os
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

class StatisticsService:
    def __init__(self):
        from services.db_svc import db_svc
        self.db_svc = db_svc

    def get_complex_stats(self, complex_name: str, area_bucket: float = None):
        """SQLite DB에서 특정 단지의 실거래 통계(중위값, 건수 등)를 직접 조회"""
        conn = self.db_svc.get_connection()
        try:
            cursor = conn.cursor()
            try:
                # 1. 먼저 Complex ID 찾기 (complex_name 기준)
                cursor.execute("SELECT complex_id FROM complex_master WHERE complex_name LIKE ?", (f"%{complex_name}%",))
                row = cursor.fetchone()
                
            except sqlite3.OperationalError as e:
                if "no such table" in str(e).lower():
                    # 테이블이 없으면 DB 초기화 재시도
                    from services.db_svc import db_svc
                    db_svc._init_db()
                    cursor.execute("SELECT complex_id FROM complex_master WHERE complex_name LIKE ?", (f"%{complex_name}%",))
                    row = cursor.fetchone()
                else:
                    raise e
            if not row:
                return None
            
            c_id = row[0]
            bucket_str = f"{int(round(area_bucket))}±2" if area_bucket else "84±2"
            
            cursor.execute("""
                SELECT median_won, count, iqr_won FROM rt_stats 
                WHERE complex_id = ? AND area_bucket = ?
            """, (c_id, bucket_str))
            
            stat_row = cursor.fetchone()
            if stat_row:
                med, cnt, iqr = stat_row
                return {
                    "median": float(med),
                    "count": int(cnt),
                    "iqr": float(iqr)
                }
            return None
        finally:
            conn.close()

    def get_market_trends(self):
        """전체 매매 시장 트렌드 (SQLite 기반)"""
        conn = self.db_svc.get_connection()
        # 월별 평균가 및 거래량 집계
        query = """
            SELECT strftime('%Y-%m', trade_date) as date,
                   AVG(price_won) as mean,
                   COUNT(*) as count
            FROM transactions
            GROUP BY date
            ORDER BY date ASC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df

stats_svc = StatisticsService()
