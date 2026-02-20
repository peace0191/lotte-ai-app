from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

DB_PATH = Path("assets/system/app.db")

OTP_TTL_SECONDS = 5 * 60          # 5분
RESEND_COOLDOWN_SECONDS = 60      # 60초 내 재전송 금지(기본)
MAX_VERIFY_ATTEMPTS = 5           # 5회 실패 시 잠금

def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_otp_tables() -> None:
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS otp_challenges (
            phone TEXT PRIMARY KEY,
            code_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            last_sent_at INTEGER NOT NULL,
            verify_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until INTEGER NOT NULL DEFAULT 0
        )
        """)
        c.commit()

def _secret_pepper() -> str:
    # 서버 비밀값(환경변수/streamlit secrets로 주입 권장)
    # 없으면 개발용으로만 동작
    return os.environ.get("OTP_PEPPER", "DEV_ONLY_CHANGE_ME")

def _hash_code(phone: str, code: str, salt: str) -> str:
    # HMAC-SHA256(pepper) + salt
    msg = f"{phone}|{code}|{salt}".encode("utf-8")
    return hmac.new(_secret_pepper().encode("utf-8"), msg, hashlib.sha256).hexdigest()

def can_send(phone: str) -> tuple[bool, str]:
    init_otp_tables()
    now = int(time.time())
    with _conn() as c:
        row = c.execute("SELECT * FROM otp_challenges WHERE phone=?", (phone,)).fetchone()
        if not row:
            return True, ""
        locked_until = int(row["locked_until"])
        if locked_until and now < locked_until:
            return False, f"잠금 상태입니다. {locked_until - now}초 후 다시 시도하세요."
        last_sent_at = int(row["last_sent_at"])
        if now - last_sent_at < RESEND_COOLDOWN_SECONDS:
            return False, f"재전송은 {RESEND_COOLDOWN_SECONDS}초 후 가능합니다."
    return True, ""

def upsert_challenge(phone: str, code: str) -> None:
    init_otp_tables()
    now = int(time.time())
    salt = os.urandom(8).hex()
    code_hash = _hash_code(phone, code, salt)
    expires_at = now + OTP_TTL_SECONDS
    with _conn() as c:
        c.execute("""
        INSERT INTO otp_challenges(phone, code_hash, salt, created_at, expires_at, last_sent_at, verify_attempts, locked_until)
        VALUES (?, ?, ?, ?, ?, ?, 0, 0)
        ON CONFLICT(phone) DO UPDATE SET
            code_hash=excluded.code_hash,
            salt=excluded.salt,
            created_at=excluded.created_at,
            expires_at=excluded.expires_at,
            last_sent_at=excluded.last_sent_at,
            verify_attempts=0,
            locked_until=0
        """, (phone, code_hash, salt, now, expires_at, now))
        c.commit()

def verify_code(phone: str, code: str) -> tuple[bool, str]:
    init_otp_tables()
    now = int(time.time())
    with _conn() as c:
        row = c.execute("SELECT * FROM otp_challenges WHERE phone=?", (phone,)).fetchone()
        if not row:
            return False, "인증 요청이 없습니다. 먼저 인증번호를 발송하세요."
        locked_until = int(row["locked_until"])
        if locked_until and now < locked_until:
            return False, f"잠금 상태입니다. {locked_until - now}초 후 다시 시도하세요."
        if now > int(row["expires_at"]):
            return False, "인증번호가 만료되었습니다. 다시 발송해 주세요."

        attempts = int(row["verify_attempts"])
        if attempts >= MAX_VERIFY_ATTEMPTS:
            # 잠금 10분
            lock = now + 10 * 60
            c.execute("UPDATE otp_challenges SET locked_until=? WHERE phone=?", (lock, phone))
            c.commit()
            return False, "시도 횟수를 초과했습니다. 10분 후 다시 시도하세요."

        salt = row["salt"]
        expected = row["code_hash"]
        got = _hash_code(phone, code, salt)

        if hmac.compare_digest(expected, got):
            # 성공 시 챌린지 삭제(재사용 방지)
            c.execute("DELETE FROM otp_challenges WHERE phone=?", (phone,))
            c.commit()
            return True, "인증 성공"
        else:
            attempts += 1
            c.execute("UPDATE otp_challenges SET verify_attempts=? WHERE phone=?", (attempts, phone))
            c.commit()
            return False, f"인증번호가 올바르지 않습니다. ({attempts}/{MAX_VERIFY_ATTEMPTS})"
