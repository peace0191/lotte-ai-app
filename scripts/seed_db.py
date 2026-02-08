import os
import sqlite3
import datetime

# Robust path resolution (v4.32)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "market_data.db")

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure tables exist (v4.33)
    cursor.execute("CREATE TABLE IF NOT EXISTS complex_master (complex_id TEXT PRIMARY KEY, name TEXT, district TEXT, standard_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS real_transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, complex_id TEXT, area_sqm REAL, price_won INTEGER, floor INTEGER, deal_date TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS complex_stats (complex_id TEXT, area_bucket TEXT, rt_median_180d INTEGER, rt_count_180d INTEGER, rt_iqr INTEGER, last_updated TEXT, PRIMARY KEY(complex_id, area_bucket))")

    # 1. 단지 마스터 정보 (표준화)
    complexes = [
        ('APT_RDP', '래미안대치팰리스', '대치동', '래미안대치팰리스'),
        ('APT_SKV', '대치SK뷰', '대치동', '대치SK뷰'),
        ('APT_ENM', '대치은마', '대치동', '대치은마')
    ]
    cursor.executemany("INSERT OR REPLACE INTO complex_master VALUES (?, ?, ?, ?)", complexes)

    # 2. 최근 180일 실거래 샘플 데이터
    # 래미안대치팰리스 84㎡ (중위가 약 32~34억 형성)
    today = datetime.date.today()
    transactions = []
    
    # 래미안대치팰리스 샘플 (15건)
    for i in range(15):
        date = today - datetime.timedelta(days=i*10)
        price = 3300000000 + (i % 5) * 50000000 # 33억 ~ 35억 사이
        transactions.append(('APT_RDP', 84.5, price, 10 + (i % 15), date.isoformat()))
        
    # 대치SK뷰 샘플 (10건)
    for i in range(10):
        date = today - datetime.timedelta(days=i*15)
        price = 3100000000 + (i % 3) * 30000000 # 31억 ~ 32억 사이
        transactions.append(('APT_SKV', 84.2, price, 5 + (i % 20), date.isoformat()))

    cursor.executemany("""
        INSERT INTO real_transactions (complex_id, area_sqm, price_won, floor, deal_date) 
        VALUES (?, ?, ?, ?, ?)
    """, transactions)

    conn.commit()
    conn.close()
    print("Seed data inserted successfully.")

if __name__ == "__main__":
    seed_data()
