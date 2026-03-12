"""
pages/96_kpi_dashboard.py
=========================
운영 KPI 대시보드 (관리자 전용).
집계 항목: 검수요청 → 승인 → 발행(성공/실패) → 예약확정 퍼널
데이터 소스: assets/system/reports/kpi_daily_YYYYMMDD.csv
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from services.rbac import require_role, sidebar_role_badge
except ImportError:
    def require_role(role): pass          # type: ignore
    def sidebar_role_badge(): pass        # type: ignore

try:
    from services.kpi_report import write_daily_csv, load_recent_kpi, build_daily_kpi
except ImportError:
    write_daily_csv  = None  # type: ignore
    load_recent_kpi  = None  # type: ignore
    build_daily_kpi  = None  # type: ignore

# ─────────────────────────────────────────────────────────
st.set_page_config(page_title="📊 KPI 대시보드", layout="wide")
sidebar_role_badge()
require_role("admin")

st.title("📊 운영 KPI 대시보드")
st.caption("운영 DB 기반 | 검수 → 승인 → 발행 → 예약 퍼널 자동 집계")

# ─────────────────────────────────────────────────────────
# 상단 버튼: 오늘 리포트 즉시 생성
# ─────────────────────────────────────────────────────────
btn_col, info_col = st.columns([2, 5])
with btn_col:
    if st.button("🔄 오늘 KPI 지금 생성", use_container_width=True):
        if write_daily_csv:
            try:
                path = write_daily_csv(datetime.now())
                st.success(f"생성 완료: {path.name}")
                st.rerun()
            except Exception as e:
                st.error(f"생성 실패: {e}")
        else:
            st.error("kpi_report 모듈을 찾을 수 없습니다.")

with info_col:
    st.info(
        "📌 매일 23:55 systemd 타이머가 자동 생성합니다. "
        "위 버튼으로 수동 즉시 생성도 가능합니다."
    )

st.divider()

# ─────────────────────────────────────────────────────────
# 오늘 실시간 KPI (DB 직접 조회)
# ─────────────────────────────────────────────────────────
st.subheader("⚡ 오늘 실시간 현황")

if build_daily_kpi:
    try:
        today_kpi = build_daily_kpi(datetime.now())
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("검수 요청",   today_kpi.get("audit_request_review", 0))
        m2.metric("승인",        today_kpi.get("audit_approve", 0))
        m3.metric("발행 성공",   today_kpi.get("publish_ok", 0))
        m4.metric("발행 실패",   today_kpi.get("publish_fail", 0))
        m5.metric("예약 확정",   today_kpi.get("reservation_confirmed", 0))

        # 퍼널 전환율
        r1, r2, r3 = st.columns(3)
        r1.metric("검수→승인율",  today_kpi.get("rate_review_to_approve",  "-"))
        r2.metric("승인→발행율",  today_kpi.get("rate_approve_to_publish", "-"))
        r3.metric("발행→예약율",  today_kpi.get("rate_publish_to_reserve", "-"))

    except Exception as e:
        st.warning(f"실시간 KPI 조회 실패: {e}")
else:
    st.warning("kpi_report 모듈이 없습니다.")

st.divider()

# ─────────────────────────────────────────────────────────
# 최근 30일 트렌드 차트
# ─────────────────────────────────────────────────────────
st.subheader("📈 최근 30일 트렌드")

REPORT_DIR = Path("assets/system/reports")
files = sorted(REPORT_DIR.glob("kpi_daily_*.csv"), reverse=True)

if not files:
    st.info(
        "아직 리포트 CSV가 없습니다. "
        "위 '오늘 KPI 지금 생성' 버튼을 눌러주세요."
    )
    st.stop()

# CSV 로드
try:
    dfs = []
    for f in files[:30]:
        try:
            dfs.append(pd.read_csv(f, encoding="utf-8-sig"))
        except Exception:
            pass

    if not dfs:
        st.warning("CSV를 읽을 수 없습니다.")
        st.stop()

    df = pd.concat(dfs, ignore_index=True).sort_values("date")

    # ── 퍼널 라인차트 ──────────────────────────────────
    chart_cols = [
        "audit_request_review",
        "audit_approve",
        "publish_ok",
        "publish_fail",
        "reservation_confirmed",
    ]
    available = [c for c in chart_cols if c in df.columns]
    if available:
        st.line_chart(df.set_index("date")[available])

    st.caption("범례: 검수요청 / 승인 / 발행성공 / 발행실패 / 예약확정")

    st.divider()

    # ── 워크플로우 현황 바차트 ──────────────────────────
    st.subheader("🔵 워크플로우 상태 현황 (누적 스냅샷)")
    wf_cols = ["wf_draft", "wf_review", "wf_approved", "wf_published", "wf_rejected"]
    wf_avail = [c for c in wf_cols if c in df.columns]
    if wf_avail:
        st.bar_chart(df.set_index("date")[wf_avail])

    st.divider()

    # ── 전체 데이터 테이블 ──────────────────────────────
    st.subheader("📋 전체 데이터")
    with st.expander("데이터 테이블 펼치기"):
        st.dataframe(df, use_container_width=True, hide_index=True)
        # CSV 다운로드
        csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="⬇️ 전체 CSV 다운로드",
            data=csv_bytes,
            file_name=f"kpi_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

except Exception as e:
    st.error(f"데이터 로드 중 오류: {e}")
