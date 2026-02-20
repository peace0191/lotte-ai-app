"""
pages/properties.py
===================
매물 목록 + 상세 통합 페이지.

핵심 기능:
  - /p/<id> 딥링크 100% 지원 (nginx → /?pid=<id> → 세션)
  - 목록 ↔ 상세 전환 (selected_property_id 세션 통일)
  - landing_url 자동 주입 + 카카오 공유 자동 활성
  - 이미지/영상 미리보기
  - 관리자/일반 사용자 흐름 분리
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# ── 프로젝트 서비스 ───────────────────────────────────────
from services.meta_ops import (
    read_meta,
    write_meta,
    ensure_landing_url,
    list_all_property_ids,
)
from services.url_builder import build_property_landing_url

try:
    from services.rbac import sidebar_role_badge, get_current_role
except ImportError:
    def sidebar_role_badge(): pass       # type: ignore
    def get_current_role(): return "guest"  # type: ignore

try:
    from services.assets_store import ensure_property_tree
except ImportError:
    def ensure_property_tree(pid): return None  # type: ignore

try:
    from services.db import get_workflow
except ImportError:
    # Fallback default workflow getter
    def get_workflow(pid): return {}     # type: ignore
except Exception: 
    def get_workflow(pid): return {}

try:
    from services.config_loader import get_config
except ImportError:
    def get_config(): return {}          # type: ignore


# ─────────────────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🏠 매물",
    layout="wide",
    initial_sidebar_state="expanded",
)
sidebar_role_badge()

# ── 세션 표준 키 ──────────────────────────────────────────
_KEY_SELECTED = "selected_property_id"
_KEY_DEEPLINK = "deeplink_pid"


# ─────────────────────────────────────────────────────────
# 딥링크 처리 — /p/<id> → /?pid=<id> → 세션 동기화
# ─────────────────────────────────────────────────────────

def _sync_pid_from_url() -> None:
    """URL query param ?pid=<id>를 세션에 동기화합니다."""
    # Handle both string and list return types from query_params.get for compatibility
    pid = st.query_params.get("pid", "")
    if isinstance(pid, list):
        pid = pid[0] if pid else ""
    pid = (pid or "").strip()
    if pid:
        st.session_state[_KEY_SELECTED] = pid
        st.session_state[_KEY_DEEPLINK] = pid


def _set_selected(pid: str) -> None:
    """매물 선택 — 세션 + URL 동시 세팅."""
    st.session_state[_KEY_SELECTED] = pid
    if pid:
        st.query_params["pid"] = pid
    else:
        # Compatibility with new and old streamlit query param methods
        if "pid" in st.query_params:
            try:
                # New api: dict-like map, might need special handling to delete?
                # Actually st.query_params is a mutable mapping in recent versions.
                del st.query_params["pid"]
            except:
                pass 
        


def _clear_selected() -> None:
    """선택 해제 — 세션 + URL 초기화."""
    _set_selected("")


def _get_selected() -> str:
    return (st.session_state.get(_KEY_SELECTED) or "").strip()


# ─────────────────────────────────────────────────────────
# Meta 헬퍼
# ─────────────────────────────────────────────────────────

def _ensure_meta_with_url(pid: str) -> Dict[str, Any]:
    """meta 읽기 + landing_url 없으면 자동 주입 + 저장."""
    meta = read_meta(pid) or {}
    original_url = meta.get("landing_url", "")
    meta = ensure_landing_url(pid, meta)
    if meta.get("landing_url") and meta.get("landing_url") != original_url:
        write_meta(pid, meta)
    return meta


def _meta_brief(pid: str) -> Dict[str, Any]:
    """목록 카드에 필요한 요약 정보만 추출."""
    meta = read_meta(pid) or {}
    title   = meta.get("title") or meta.get("name") or f"매물 {pid}"
    address = meta.get("address") or ""
    gap     = meta.get("market_gap_percent")
    vip     = meta.get("vip_hot") is True or (
        isinstance(meta.get("vip_score"), (int, float)) and float(meta.get("vip_score", 0)) > 0
    )
    return {
        "pid":         pid,
        "title":       title,
        "address":     address,
        "gap":         gap,
        "vip":         vip,
        "landing_url": meta.get("landing_url", ""),
        "status":      meta.get("status", "draft"),
    }


# ─────────────────────────────────────────────────────────
# 상세 화면 렌더링
# ─────────────────────────────────────────────────────────

def _render_detail(pid: str) -> None:
    meta        = _ensure_meta_with_url(pid)
    title       = meta.get("title") or meta.get("name") or f"매물 {pid}"
    address     = meta.get("address") or ""
    gap         = meta.get("market_gap_percent")
    landing_url = meta.get("landing_url", "")
    role        = get_current_role()

    # ── 헤더 ────────────────────────────────────────────
    vip_badge = "🔥 " if meta.get("vip_hot") else ""
    st.subheader(f"{vip_badge}🏠 {title}")
    if address:
        st.caption(f"📍 {address}")

    # ── 상태 배지 ────────────────────────────────────────
    wf     = get_workflow(pid) or {}
    status = wf.get("status") or meta.get("status", "draft")
    STATUS_COLOR = {
        "draft":     "🔵",
        "review":    "🟡",
        "approved":  "🟢",
        "published": "✅",
        "rejected":  "🔴",
    }
    st.write(f"{STATUS_COLOR.get(status, '⚪')} 상태: **{status}**")

    st.divider()

    # ── 핵심 지표 ────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("매물 ID", pid)
    with col2:
        # gap could be None
        st.metric("저평가(%)", f"{gap}%" if gap not in (None, "") else "-")
    with col3:
        st.metric("VIP_HOT", "🔥 YES" if meta.get("vip_hot") else "NO")
    with col4:
        vip_score = meta.get("vip_score")
        st.metric("VIP Score", str(vip_score) if vip_score not in (None, "") else "-")

    # ── 고정 URL ─────────────────────────────────────────
    if landing_url:
        st.link_button("🔗 고정 상세 URL (/p/<id>)", landing_url, use_container_width=True)
        st.code(landing_url, language=None)

    st.divider()

    # ── 탭: 이미지 / 영상 / 메타 / 카카오 공유 ──────────
    tabs = st.tabs(["🖼️ 사진", "🎬 영상", "📋 메타 정보", "💬 카카오 공유"])

    paths = ensure_property_tree(pid)

    # 탭 1: 이미지
    with tabs[0]:
        imgs: List[Path] = []
        # Modified to use correct attribute names: processed_photos, raw_photos based on assets_store.py
        for attr in ["processed_photos", "raw_photos"]:
            folder = getattr(paths, attr, None) if paths else None
            # If attr not found, getattr returns None
            if folder and Path(folder).exists():
                imgs += sorted(Path(folder).glob("*.jpg"))
                imgs += sorted(Path(folder).glob("*.jpeg"))
                imgs += sorted(Path(folder).glob("*.png"))
        if imgs:
            st.image([str(p) for p in imgs[:12]], use_container_width=True)
            if len(imgs) > 12:
                st.caption(f"총 {len(imgs)}장 중 12장만 표시")
        else:
            st.info("이미지가 없습니다. 미디어 업로드 센터에서 등록하세요.")

    # 탭 2: 영상
    with tabs[1]:
        vids: List[Path] = []
        # Correct attributes: processed_videos, raw_videos (match assets_store.py)
        for attr in ["processed_videos", "raw_videos"]:
            folder = getattr(paths, attr, None) if paths else None
            if folder and Path(folder).exists():
                vids += sorted(Path(folder).glob("*.mp4"))
        if vids:
            st.video(str(vids[0]))
            if len(vids) > 1:
                with st.expander(f"다른 영상 보기 ({len(vids)-1}개)"):
                    for v in vids[1:5]:
                        st.video(str(v))
        else:
            st.info("영상이 없습니다. 미디어 업로드 센터에서 등록하세요.")

    # 탭 3: 메타 정보
    with tabs[2]:
        display_meta = {k: v for k, v in meta.items() if k not in ("__raw__",)}
        st.json(display_meta)
        if role == "admin":
            with st.expander("⚙️ 관리자: meta.json 직접 수정"):
                new_json = st.text_area(
                    "meta.json 내용 (JSON)",
                    value=json.dumps(display_meta, ensure_ascii=False, indent=2),
                    height=300,
                )
                if st.button("💾 저장", key=f"save_meta_{pid}"):
                    try:
                        updated = json.loads(new_json)
                        write_meta(pid, updated)
                        st.success("저장 완료!")
                        st.rerun()
                    except json.JSONDecodeError as e:
                        st.error(f"JSON 형식 오류: {e}")

    # 탭 4: 카카오 공유
    with tabs[3]:
        kakao_payload_path = None
        if paths:
            # Matches publish_kakao in assets_store.py
            kakao_dir = getattr(paths, "publish_kakao", None)
            if kakao_dir:
                kakao_payload_path = Path(kakao_dir) / "message_payload.json"

        if kakao_payload_path and kakao_payload_path.exists():
            try:
                payload = json.loads(kakao_payload_path.read_text(encoding="utf-8"))
                st.success("카카오 공유 준비 완료 ✅")

                msg = payload.get("message", "")
                st.text_area("📋 공유 메시지 (복사 후 카카오 전송)", msg, height=180)

                btn = payload.get("button") or {}
                if btn.get("url"):
                    st.link_button(
                        btn.get("title", "📱 상담/예약하기"),
                        btn["url"],
                        use_container_width=True,
                    )

                with st.expander("🔍 전체 Payload 보기"):
                    st.json(payload)

            except Exception as e:
                st.error(f"Payload 파싱 오류: {e}")
        else:
            st.info(
                "카카오 공유 정보가 아직 없습니다.\n\n"
                "**🚀 광고 발행 센터** → Payload 생성 → 승인 후 자동으로 활성화됩니다."
            )


# ─────────────────────────────────────────────────────────
# 목록 화면 렌더링
# ─────────────────────────────────────────────────────────

def _render_list() -> None:
    st.subheader("📋 매물 목록")

    # ── 필터 컨트롤 ─────────────────────────────────────
    col_search, col_vip, col_status = st.columns([3, 1, 1])
    with col_search:
        q = st.text_input("🔍 검색", placeholder="단지명, 주소, 매물ID…")
    with col_vip:
        only_vip = st.checkbox("🔥 VIP만", value=False)
    with col_status:
        status_filter = st.selectbox(
            "상태",
            options=["전체", "draft", "review", "approved", "published", "rejected"],
        )

    pids = list_all_property_ids()
    if not pids:
        st.warning("assets/properties/ 아래에 매물 폴더가 없습니다.")
        st.info("🧰 미디어 업로드 센터에서 신규 매물을 먼저 생성하세요.")
        return

    # ── 카드 그리기 ──────────────────────────────────────
    cards = []
    for pid in pids:
        info = _meta_brief(pid)
        # 검색 필터
        blob = f"{info['pid']} {info['title']} {info['address']}".lower()
        if q and q.lower() not in blob:
            continue
        # VIP 필터
        if only_vip and not info["vip"]:
            continue
        # 상태 필터
        if status_filter != "전체" and info.get("status") != status_filter:
            continue
        cards.append(info)

    if not cards:
        st.warning("조건에 맞는 매물이 없습니다.")
        return

    st.caption(f"총 {len(cards)}건")

    STATUS_COLOR = {
        "draft":     "🔵",
        "review":    "🟡",
        "approved":  "🟢",
        "published": "✅",
        "rejected":  "🔴",
    }

    for info in cards[:200]:
        vip_badge = "🔥 " if info["vip"] else ""
        gap_txt   = f" · 저평가 {info['gap']}%" if info["gap"] not in (None, "", 0) else ""
        status_ic = STATUS_COLOR.get(info.get("status", "draft"), "⚪")

        with st.container(border=True):
            hcol, scol = st.columns([4, 1])
            with hcol:
                st.markdown(f"**{vip_badge}{info['title']}{gap_txt}**")
            with scol:
                st.caption(f"{status_ic} {info.get('status','draft')}")

            if info["address"]:
                st.caption(f"📍 {info['address']}")

            b1, b2, b3 = st.columns(3)
            with b1:
                # Key must be unique
                if st.button("🔍 상세 보기", key=f"open_{info['pid']}", use_container_width=True):
                    _set_selected(info["pid"])
                    st.rerun()
            with b2:
                if info.get("landing_url"):
                    st.link_button(
                        "🔗 공유 링크",
                        info["landing_url"],
                        use_container_width=True,
                    )
                else:
                    st.button("링크 없음", key=f"nourl_{info['pid']}", disabled=True, use_container_width=True)
            with b3:
                st.caption(f"ID: {info['pid']}")


# ─────────────────────────────────────────────────────────
# 메인 진입점
# ─────────────────────────────────────────────────────────

_sync_pid_from_url()  # ✅ 딥링크 처리 — 가장 먼저 실행

st.title("🏠 매물")
st.caption("목록/상세 통합 · /p/<id> 딥링크 지원")

selected_id = _get_selected()

if selected_id:
    # ── 뒤로가기 버튼 (상단 고정) ───────────────────────
    if st.button("⬅️ 목록으로", use_container_width=False):
        _clear_selected()
        st.rerun()

    st.divider()
    _render_detail(selected_id)

else:
    _render_list()
