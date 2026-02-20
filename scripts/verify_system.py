from __future__ import annotations

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.config_loader import load_config

def check_mark(ok: bool) -> str:
    return "✅" if ok else "❌"

def run_verification():
    print("🔍 [Lotte AI App] 시스템 무결성 및 설정 검증 시작...\n")

    # 1. 필수 디렉토리 체크
    required_dirs = [
        "assets/properties",
        "assets/system/keys",
        "assets/branding/watermark",
        "assets/branding/templates",
        "assets/branding/fonts",
        ".streamlit"
    ]
    
    print("1. 📂 필수 디렉토리 확인")
    all_dirs_ok = True
    for d in required_dirs:
        p = Path(d)
        exists = p.exists()
        print(f"   {check_mark(exists)} {d}")
        if not exists:
            all_dirs_ok = False
            # Create if missing (some are critical)
            if "branding" in d:
                p.mkdir(parents=True, exist_ok=True)
                print(f"      -> ⚠️ 생성됨 (빈 폴더)")
    print("")

    # 2. 환경변수/Secrets 체크
    print("2. 🔑 환경변수 및 API Key 설정 확인 (secrets.toml)")
    load_config()
    env_keys = [
        ("SOLAPI_API_KEY", "문자 발송"),
        ("KAKAO_JS_KEY", "카카오 공유"),
        ("OTP_PEPPER", "보안 키"),
        ("ADMIN_PHONES", "관리자 번호"),
    ]
    
    for key, label in env_keys:
        val = os.environ.get(key)
        exists = bool(val and len(val) > 1)
        # 보안상 값의 일부만 노출하거나 길이만 표시
        disp = f"{val[:4]}...({len(val)}자)" if exists else "(미설정)"
        print(f"   {check_mark(exists)} {label} ({key}): {disp}")
    
    # YouTube OAuth Key
    yt_key = Path("assets/system/keys/youtube_client_secret.json")
    print(f"   {check_mark(yt_key.exists())} YouTube OAuth Secret: {yt_key.name if yt_key.exists() else '(미보유)'}")
    print("")

    # 3. 데이터베이스 체크
    print("3. 💾 데이터베이스 연결 확인")
    db_path = Path("assets/system/app.db")
    if not db_path.exists():
        print(f"   ❌ DB 파일 없음: {db_path}")
    else:
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check tables
            tables = ["users", "otp_challenges", "property_workflows", "audit_logs", "publish_queue"]
            for t in tables:
                try:
                    cnt = cursor.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                    print(f"   ✅ Table '{t}': {cnt} rows")
                except sqlite3.OperationalError:
                    print(f"   ❌ Table '{t}': (테이블 없음)")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ DB 연결 에러: {e}")
    print("")

    print("🏁 검증 완료.")

if __name__ == "__main__":
    run_verification()
