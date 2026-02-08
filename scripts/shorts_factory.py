import os
import sqlite3
import pandas as pd
import subprocess

# Robust path resolution (v4.32)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "market_data.db")

def update_complex_statistics():
    """
    180일 실거래 데이터를 기반으로 중위값, 표본수, IQR(변동성)을 자동 계산하여 통계 테이블 업데이트
    """
    conn = sqlite3.connect(DB_PATH)
    
    # 최근 180일 거래 데이터 로드
    query = """
    SELECT complex_id, area_sqm, price_won, deal_date 
    FROM real_transactions 
    WHERE deal_date >= date('now', '-180 days')
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No transaction data Found.")
        return

    # 면적별 버킷 생성 (84sqm -> 84버킷)
    df['area_bucket'] = df['area_sqm'].round().astype(int).astype(str)
    
    # 통계 계산
    stats = df.groupby(['complex_id', 'area_bucket']).agg(
        rt_median_180d=('price_won', 'median'),
        rt_count_180d=('price_won', 'count'),
        rt_iqr=('price_won', lambda x: x.quantile(0.75) - x.quantile(0.25))
    ).reset_index()
    
    # DB 업데이트
    for _, row in stats.iterrows():
        conn.execute("""
            INSERT OR REPLACE INTO complex_stats 
            (complex_id, area_bucket, rt_median_180d, rt_count_180d, rt_iqr, last_updated)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (row.complex_id, row.area_bucket, int(row.rt_median_180d), int(row.rt_count_180d), int(row.rt_iqr)))
    
    conn.commit()
    conn.close()
    print("Market Statistics Updated Successfully.")

def synthesize_shorts_ffmpeg(video_path, audio_path, script_lines, output_name):
    """
    FFmpeg를 사용하여 영상 + 오디오 + 자막(Script)을 합성하는 기본 코드
    """
    # [주의] 시스템에 ffmpeg가 설치되어 있어야 합니다.
    # 단순 예시: 영상 위에 자막 입히기 (Drawtext 필터)
    drawtext_filter = f"drawtext=text='{script_lines[0]}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-100:enable='between(t,0,3)'"
    
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-filter_complex', drawtext_filter,
        '-map', '0:v', '-map', '1:a',
        '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p',
        output_name
    ]
    
    # subprocess.run(cmd) # 실제 실행 시 주석 해제
    print(f"FFmpeg Command Generated for: {output_name}")

if __name__ == "__main__":
    update_complex_statistics()
