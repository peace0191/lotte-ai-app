from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DB_PATH = Path("assets/system/app.db")
MAX_ATTEMPTS_DEFAULT = 3

def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_column(c: sqlite3.Connection, table: str, col: str, ddl: str):
    # SQLite: PRAGMA table_info로 컬럼 존재 여부 체크 후 ALTER TABLE
    cols = [r["name"] for r in c.execute(f"PRAGMA table_info({table})").fetchall()]
    if col not in cols:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

def init_publish_queue():
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS publish_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at INTEGER NOT NULL,
            due_at INTEGER NOT NULL,
            status TEXT NOT NULL,            -- queued|running|done|failed
            property_id TEXT NOT NULL,
            channel TEXT NOT NULL,           -- youtube|kakao|sns
            payload_path TEXT NOT NULL,      -- publish/youtube/upload_payload.json 등
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            last_error TEXT DEFAULT '',
            priority INTEGER NOT NULL DEFAULT 0  -- ✅ VIP_HOT 우선순위 (높을수록 먼저)
        )
        """)
        # ✅ 기존 DB 마이그레이션: priority 컬럼 없으면 추가
        _ensure_column(c, "publish_queue", "priority", "priority INTEGER NOT NULL DEFAULT 0")
        c.commit()

def enqueue(property_id: str, channel: str, payload_path: str, due_at: Optional[int] = None,
            max_attempts: int = MAX_ATTEMPTS_DEFAULT, priority: int = 0) -> int:
    init_publish_queue()
    now = int(time.time())
    due = int(due_at or now)
    with _conn() as c:
        cur = c.execute("""
        INSERT INTO publish_queue(created_at, due_at, status, property_id, channel, payload_path, attempts, max_attempts, priority)
        VALUES (?, ?, 'queued', ?, ?, ?, 0, ?, ?)
        """, (now, due, property_id, channel, payload_path, int(max_attempts), int(priority)))
        c.commit()
        return int(cur.lastrowid)

def list_queue(limit: int = 200) -> List[Dict[str, Any]]:
    init_publish_queue()
    with _conn() as c:
        rows = c.execute("""
        SELECT * FROM publish_queue
        ORDER BY due_at ASC, priority DESC, id ASC
        LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

def fetch_due_jobs(limit: int = 10) -> List[Dict[str, Any]]:
    init_publish_queue()
    now = int(time.time())
    with _conn() as c:
        rows = c.execute("""
        SELECT * FROM publish_queue
        WHERE status='queued' AND due_at<=?
        ORDER BY due_at ASC, priority DESC, id ASC
        LIMIT ?
        """, (now, limit)).fetchall()
        return [dict(r) for r in rows]

def mark_running(job_id: int) -> None:
    init_publish_queue()
    with _conn() as c:
        c.execute("UPDATE publish_queue SET status='running' WHERE id=?", (job_id,))
        c.commit()

def mark_done(job_id: int) -> None:
    init_publish_queue()
    with _conn() as c:
        c.execute("UPDATE publish_queue SET status='done', last_error='' WHERE id=?", (job_id,))
        c.commit()

def mark_failed(job_id: int, error: str, retry_in_seconds: Optional[int] = None) -> None:
    init_publish_queue()
    now = int(time.time())
    with _conn() as c:
        row = c.execute("SELECT * FROM publish_queue WHERE id=?", (job_id,)).fetchone()
        if not row:
            return
        job = dict(row)
        attempts = int(job["attempts"]) + 1
        max_attempts = int(job["max_attempts"])
        err = (error or "")[:500]

        if attempts >= max_attempts:
            c.execute("""
            UPDATE publish_queue
            SET status='failed', attempts=?, last_error=?
            WHERE id=?
            """, (attempts, err, job_id))
        else:
            backoff = int(retry_in_seconds or _default_backoff(attempts))
            due_at = now + backoff
            c.execute("""
            UPDATE publish_queue
            SET status='queued', attempts=?, due_at=?, last_error=?
            WHERE id=?
            """, (attempts, due_at, err, job_id))
        c.commit()

def _default_backoff(attempts: int) -> int:
    if attempts <= 1:
        return 5 * 60
    if attempts == 2:
        return 15 * 60
    return 60 * 60
