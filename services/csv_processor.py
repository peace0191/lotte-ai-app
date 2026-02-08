import pandas as pd
import glob
import os
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def area_bucket(area_sqm: float, tol: int = 2) -> str:
    if pd.isna(area_sqm): return "84±2"
    base = int(round(area_sqm))
    return f"{base}±{tol}"

def pick_column(df, candidates):
    for c in candidates:
        if c in df.columns: return c
    return None

def process_csv_files():
    import sys
    sys.path.append(str(BASE_DIR))
    try:
        from services.db_svc import db_svc
    except ImportError:
        import db_svc
    
    # CSV 및 Excel 파일 모두 검색
    data_files = glob.glob(str(BASE_DIR / "*.csv")) + glob.glob(str(BASE_DIR / "*.xlsx")) + glob.glob(str(BASE_DIR / "*.xls"))
    summary = {"ingested": 0, "skipped": 0, "total_rows": 0, "errors": []}
    
    conn = db_svc.get_connection()
    cursor = conn.cursor()

    for f in data_files:
        filename = os.path.basename(f)
        file_hash = calculate_sha256(f)
        
        # 중복 방지 체크
        cursor.execute("SELECT 1 FROM ingested_files WHERE sha256 = ?", (file_hash,))
        if cursor.fetchone():
            summary["skipped"] += 1
            continue

        try:
            df = None
            # 1. Excel 처리
            if filename.endswith(('.xlsx', '.xls')):
                try:
                    # 국토부 엑셀은 보통 첫 몇 줄이 헤더 정보일 수 있음
                    temp_df = pd.read_excel(f, nrows=20)
                    header_idx = 0
                    for i, row in temp_df.iterrows():
                        row_str = " ".join(map(str, row.values))
                        if any(k in row_str for k in ['단지명', '아파트', '오피스텔', '건물명', '거래금액']):
                            header_idx = i
                            break
                    df = pd.read_excel(f, skiprows=header_idx)
                except Exception as e:
                    summary["errors"].append(f"{filename} (Excel): {str(e)}")
                    continue
            
            # 2. CSV 처리
            else:
                encodings = ['cp949', 'utf-8-sig', 'euc-kr', 'utf-8']
                header_idx = -1
                for enc in encodings:
                    try:
                        with open(f, 'r', encoding=enc, errors='ignore') as temp_f:
                            lines = temp_f.readlines()
                            for i, line in enumerate(lines[:30]): # 상위 30줄 검사
                                if (line.count(',') > 5) and (any(k in line for k in ['단지명', '아파트', '오피스텔', '건물명', '거래금액'])):
                                    header_idx = i
                                    break
                        if header_idx != -1:
                            df = pd.read_csv(f, encoding=enc, skiprows=header_idx, on_bad_lines='skip')
                            break
                    except:
                        continue
            
            if df is None or df.empty:
                summary["errors"].append(f"{filename}: 데이터가 없거나 형식을 알 수 없음")
                continue

            # 컬럼명 정제
            df.columns = [str(c).strip().replace('"', '').replace(' ', '') for c in df.columns]
            
            # --- 고도화된 컬럼 매칭 (v5.0 Upgrade) ---
            name_col = pick_column(df, ['단지명', '아파트', '오피스텔', '건물명', '상호', '단지'])
            price_col = pick_column(df, ['거래금액(만원)', '보증금(만원)', '매매가', '거래금액', '가격', '금액'])
            area_col = pick_column(df, ['전용면적(㎡)', '전용면적', '평형', '계약면적(㎡)', '면적'])
            ym_col = pick_column(df, ['계약년월', '거래년월', '연월', '계약일자'])
            day_col = pick_column(df, ['계약일', '거래일', '날짜'])
            dong_col = pick_column(df, ['법정동', '시군구', '지역', '주소', '동'])

            # 인덱스 기반 Fallback (표준 국토부 양식)
            if not name_col and len(df.columns) >= 10:
                name_col = df.columns[5]
                area_col = df.columns[6]
                ym_col = df.columns[7]
                day_col = df.columns[8]
                price_col = df.columns[9]
                dong_col = df.columns[1]

            if not all([name_col, price_col, area_col, ym_col]):
                summary["errors"].append(f"{filename}: 필수 컬럼 누락 ({name_col}, {price_col}, {area_col})")
                continue

            # 3. 데이터 정제 및 적재
            rows_added = 0
            for idx, row in df.iterrows():
                try:
                    c_name = str(row[name_col]).strip()
                    if not c_name or c_name == 'nan' or len(c_name) < 2: continue
                    
                    c_id = f"CMPX_{abs(hash(c_name)) % 1000000}"
                    
                    # 가격 변환 (만원 단위 정수)
                    p_val = str(row[price_col]).replace(',', '').replace('"', '').strip()
                    if not p_val or p_val == 'nan': continue
                    price_val = int(float(p_val))
                    
                    # 날짜 변환
                    ym_val = str(row[ym_col]).strip()
                    d_val = str(row[day_col]).strip() if day_col else "01"
                    if len(ym_val) >= 6:
                        d_str = d_val.zfill(2) if d_val.isdigit() else "01"
                        t_date = f"{ym_val[:4]}-{ym_val[4:6]}-{d_str[:2]}"
                    else:
                        t_date = datetime.now().strftime("%Y-%m-%d")

                    # 면적 변환
                    import re
                    area_val = 84.0
                    area_str = str(row[area_col]).replace(',', '')
                    area_match = re.search(r'(\d+\.?\d*)', area_str)
                    if area_match:
                        area_val = float(area_match.group(1))

                    floor_val = 0
                    if '층' in df.columns:
                        try: floor_val = int(float(str(row['층']).strip()))
                        except: pass

                    # DB 저장
                    dong_val = str(row.get(dong_col, '대치동')).split()[-1]
                    cursor.execute("INSERT OR IGNORE INTO complex_master (complex_id, complex_name, dong) VALUES (?, ?, ?)", 
                                   (c_id, c_name, dong_val))
                    
                    cursor.execute("""
                        INSERT INTO transactions (complex_id, trade_date, area_sqm, floor, price_won) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (c_id, t_date, area_val, floor_val, price_val))
                    rows_added += 1
                except Exception:
                    continue

            # 파일 이력 기록
            cursor.execute("INSERT INTO ingested_files (sha256, file_path, ingested_at) VALUES (?, ?, ?)",
                           (file_hash, filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            summary["ingested"] += 1
            summary["total_rows"] += rows_added
            
        except Exception as e:
            summary["errors"].append(f"{filename}: {str(e)}")
            
    conn.commit()
    build_db_stats(conn)
    conn.close()
    
    with open(DATA_DIR / "csv_summary.json", "w", encoding="utf-8") as jf:
        json.dump(summary, jf, ensure_ascii=False, indent=2)

def build_db_stats(conn):
    cursor = conn.cursor()
    # 최근 2년 데이터로 통계 계산 (사용자 요청 반영: 신뢰도 향상)
    cursor.execute("""
        SELECT complex_id, area_sqm, price_won FROM transactions 
        WHERE trade_date >= date('now', '-730 days')
    """)
    rows = cursor.fetchall()
    
    groups = {}
    for c_id, area, price in rows:
        bucket = area_bucket(area)
        key = (c_id, bucket)
        if key not in groups: groups[key] = []
        groups[key].append(price)
        
    for (c_id, bucket), prices in groups.items():
        if not prices: continue
        prices_s = sorted(prices)
        median = prices_s[len(prices_s)//2]
        count = len(prices_s)
        iqr = 0
        if count >= 4:
            q3 = prices_s[int(count*0.75)]
            q1 = prices_s[int(count*0.25)]
            iqr = q3 - q1
        
        cursor.execute("""
            INSERT OR REPLACE INTO rt_stats (complex_id, area_bucket, window_days, median_won, count, iqr_won, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (c_id, bucket, 730, int(median), count, int(iqr), datetime.now().strftime("%Y-%m-%d")))
    conn.commit()

if __name__ == "__main__":
    try:
        process_csv_files()
    except Exception as e:
        print(f"Standalone execution error: {e}")
