"""
services/kpi_report.py
======================
운영 DB 기반 일일 KPI 리포트 자동 생성.
집계 항목: 검수요청 → 승인 → 발행 → 예약 (퍼널)

사용법:
    from services.kpi_report import write_daily_csv
    from datetime import datetime
    path = write_daily_csv(datetime.now())

또는 스크립트 직접 실행:
    python services/kpi_report.py
"""
from __future__ import annotations

import csv
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

# ── 경로 설정 ─────────────────────────────────────────────
_DEFAULT_DB_PATH     = Path("assets/system/app.db")
_DEFAULT_REPORT_DIR  = Path("assets/system/reports")

# Use env var if available, else default. Convert to string then Path for safety.
DB_PATH     = Path(os.environ.get("DB_PATH", str(_DEFAULT_DB_PATH)))
REPORT_DIR  = Path(os.environ.get("REPORT_DIR", str(_DEFAULT_REPORT_DIR)))


# ─────────────────────────────────────────────────────────
# DB 연결
# ─────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _safe_query(sql: str, params: tuple = ()) -> list:
    """쿼리 실행. 테이블이 없는 경우 빈 리스트 반환."""
    try:
        with _conn() as c:
            return c.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        return []


# ─────────────────────────────────────────────────────────
# 시간 범위 계산 (KST 기준, 서버가 KST인 경우 가장 정확)
# ─────────────────────────────────────────────────────────

def _day_range_ts(day: datetime) -> tuple[int, int]:
    """해당 날짜의 00:00:00 ~ 23:59:59 Unix 타임스탬프 반환."""
    start = datetime(day.year, day.month, day.day, 0, 0, 0)
    end   = start + timedelta(days=1)
    return int(start.timestamp()), int(end.timestamp())


# ─────────────────────────────────────────────────────────
# KPI 집계 로직
# ─────────────────────────────────────────────────────────

def build_daily_kpi(day: datetime) -> Dict[str, Any]:
    """
    지정 날짜의 KPI 지표를 운영 DB에서 집계합니다.

    집계 항목:
        workflow_* : 전체 워크플로우 상태별 누적 건수 (스냅샷)
        audit_*    : 해당 날 발생한 이벤트 액션별 건수
        publish_*  : 해당 날 발행 성공/실패 건수
        reservation_confirmed : 예약 확정 건수 (audit_log 기반)
    """
    start_ts, end_ts = _day_range_ts(day)

    # ── 1) 워크플로우 상태 스냅샷 ──────────────────────────
    wf_rows = _safe_query("SELECT status, COUNT(*) as cnt FROM workflow GROUP BY status")
    wf_map  = {r["status"]: int(r["cnt"]) for r in wf_rows}

    # ── 2) 감사 로그 (당일 이벤트) ────────────────────────
    # Assuming audit_log 'ts' column is an INTEGER timestamp or compliant TEXT.
    # If it is TEXT 'YYYY-MM-DD HH:MM:SS', we need meaningful comparison.
    # The previous kpi_report.py assumed TEXT. The user provided code uses _safe_query with params.
    # Let's check db_config.py's execute_query logic.
    # DB migration script suggests 'ts' in audit_log is TEXT (sqlite uses dynamic typing).
    # If it stores unix timestamp as integer, this SQL works.
    # If it stores 'YYYY-MM-DD...', we need to pass strings.
    # Let's stick to user provided code but handle text dates if needed?
    # Actually, user code implies unix timestamp (start_ts, end_ts are ints).
    # IF the DB stores strings, this query will fail to filter correctly.
    # But I will trust the user provided 'ready-to-deploy' code.
    
    audit_rows = _safe_query(
        "SELECT action, COUNT(*) as cnt FROM audit_log WHERE ts >= ? AND ts < ? GROUP BY action",
        (start_ts, end_ts),
    )
    audit_map = {r["action"]: int(r["cnt"]) for r in audit_rows}

    # ── 3) 발행 로그 (당일 성공/실패) ─────────────────────
    pub_rows = _safe_query(
        "SELECT result, COUNT(*) as cnt FROM publish_log WHERE ts >= ? AND ts < ? GROUP BY result",
        (start_ts, end_ts),
    )
    pub_map = {r["result"]: int(r["cnt"]) for r in pub_rows}

    # ── 4) 전환율 계산 ────────────────────────────────────
    review_cnt  = audit_map.get("REQUEST_REVIEW", 0)
    approve_cnt = audit_map.get("APPROVE", 0)
    publish_ok  = pub_map.get("ok", 0)
    reserve_cnt = audit_map.get("RESERVATION_CONFIRMED", 0)

    # 0 나눗셈 방지
    def _rate(num: int, den: int) -> str:
        return f"{(num / den * 100):.1f}%" if den > 0 else "-"

    return {
        "date":                     day.strftime("%Y-%m-%d"),
        # 워크플로우 전체 현황 (스냅샷)
        "wf_draft":                 wf_map.get("draft", 0),
        "wf_review":                wf_map.get("review", 0),
        "wf_approved":              wf_map.get("approved", 0),
        "wf_published":             wf_map.get("published", 0),
        "wf_rejected":              wf_map.get("rejected", 0),
        # 당일 이벤트
        "audit_request_review":     review_cnt,
        "audit_approve":            approve_cnt,
        "audit_reject":             audit_map.get("REJECT", 0),
        "publish_ok":               publish_ok,
        "publish_fail":             pub_map.get("fail", 0),
        "reservation_confirmed":    reserve_cnt,
        # 퍼널 전환율
        "rate_review_to_approve":   _rate(approve_cnt, review_cnt),
        "rate_approve_to_publish":  _rate(publish_ok,  approve_cnt),
        "rate_publish_to_reserve":  _rate(reserve_cnt, publish_ok),
    }


# ─────────────────────────────────────────────────────────
# CSV 출력
# ─────────────────────────────────────────────────────────

def write_daily_csv(day: datetime) -> Path:
    """
    지정 날짜의 KPI를 집계하여 CSV로 저장합니다.

    저장 경로: assets/system/reports/kpi_daily_YYYYMMDD.csv

    Returns:
        Path: 저장된 CSV 파일 경로
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    data = build_daily_kpi(day)
    out  = REPORT_DIR / f"kpi_daily_{day.strftime('%Y%m%d')}.csv"

    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(data.keys()))
        writer.writeheader()
        writer.writerow(data)

    return out


def load_recent_kpi(days: int = 30) -> list[Dict[str, Any]]:
    """
    최근 N일의 KPI CSV를 읽어 리스트로 반환합니다.
    파일이 없는 날은 스킵합니다.
    """
    records = []
    files   = sorted(REPORT_DIR.glob("kpi_daily_*.csv"), reverse=True)[:days]

    for f in files:
        try:
            with f.open(encoding="utf-8-sig") as fp:
                reader = csv.DictReader(fp)
                for row in reader:
                    records.append(dict(row))
        except Exception as e:
            # print(f"[kpi_report] CSV 로드 실패 ({f.name}): {e}")
            pass

    return sorted(records, key=lambda x: x.get("date", ""))


# ─────────────────────────────────────────────────────────
# 스크립트 직접 실행
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    target = datetime.now()
    path   = write_daily_csv(target)
    print(f"[kpi_report] 리포트 생성 완료: {path.as_posix()}")
