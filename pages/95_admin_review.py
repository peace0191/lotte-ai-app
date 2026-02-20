from __future__ import annotations

from pathlib import Path
import json

import time

import streamlit as st

from services.auth_helper import require_role
from services.assets_store import ensure_property_tree, list_property_ids
from services.db import set_workflow, get_workflow, list_workflows, audit

st.set_page_config(page_title="✅ 관리자 검수/승인", layout="wide")
auth = require_role("admin")

st.title("✅ 관리자 검수/승인 센터")
st.caption("공급자가 업로드/자동생성한 매물을 관리자(공인중개사)가 검수 후 승인/보류합니다.")

# 워크플로우 목록
wf = list_workflows(limit=200)
with st.expander("📌 전체 워크플로우(최근 순)", expanded=False):
    if not wf:
        st.info("아직 workflow 기록이 없습니다.")
    else:
        st.dataframe(wf, use_container_width=True)

ids = list_property_ids()
if not ids:
    st.warning("매물이 없습니다.")
    st.stop()

# 워크플로우가 있는 매물 우선 선택? 
# 일단 기본은 가장 최근꺼.
idx = len(ids) - 1
if "selected_property_id" in st.session_state and st.session_state.selected_property_id in ids:
    idx = ids.index(st.session_state.selected_property_id)

pid = st.selectbox("검수할 매물 선택", ids, index=idx)
st.session_state.selected_property_id = pid
paths = ensure_property_tree(pid)

w = get_workflow(pid) or {"status": "draft", "supplier_id": "", "note": ""}
st.info(f"현재 상태: **{w.get('status')}**  | 공급자: `{w.get('supplier_id','')}`  | note: {w.get('note','')}")

# meta 표시
meta_path = paths.meta_json
meta = {}
if meta_path.exists():
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        meta = {}
st.subheader("📄 meta.json")
st.json(meta)

# 산출물 미리보기(핵심)
left, right = st.columns([1, 1], vertical_alignment="top")
with left:
    st.markdown("### 🖼️ 썸네일/카카오")
    thumbs = sorted(list((paths.processed_thumbs).glob("*.jpg")))
    if thumbs:
        for p in thumbs:
            st.image(str(p), caption=p.name, use_container_width=True)
    else:
        st.warning("processed/thumbs 결과가 없습니다. (자동 생성 먼저)")

with right:
    st.markdown("### 🎞️ 숏츠 영상")
    vids = sorted(list((paths.processed_videos).glob("*.mp4")))
    if vids:
        st.video(str(vids[0]))
        st.caption(vids[0].name)
    else:
        st.warning("processed/videos 결과가 없습니다. (자동 생성 먼저)")

st.divider()

note = st.text_area("관리자 메모(보류 사유/수정 요청 등)", value=w.get("note",""), height=90)

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🔎 검수대기(review)로 전환", use_container_width=True):
        set_workflow(pid, "review", supplier_id=w.get("supplier_id") or None, note=note)
        audit(auth["user_id"], auth["role"], "SET_REVIEW", pid, note)
        st.success("review로 전환 완료")
        st.rerun()

from services.publish_queue import enqueue
from services.meta_ops import read_meta as read_meta_ops, vip_score

# ... (중략)

with c2:
    if st.button("✅ 승인(approved)", use_container_width=True):
        set_workflow(pid, "approved", supplier_id=w.get("supplier_id") or None, note=note)
        audit(auth["user_id"], auth["role"], "APPROVE", pid, note)
        
        # 🚀 큐에 자동 등록 (VIP 우선순위 적용)
        # payload_path 찾기
        payload_path = paths.publish_youtube / "upload_payload.json"
        
        if payload_path.exists():
            meta_data = read_meta_ops(pid)
            prio = vip_score(meta_data)
            
            job_id = enqueue(
                property_id=pid, 
                channel="youtube", 
                payload_path=payload_path.as_posix(), 
                due_at=None, 
                max_attempts=3, 
                priority=prio
            )
            st.success(f"approved 완료 & 큐 등록됨 (Job ID: {job_id}, Priority: {prio})")
        else:
            st.warning("approved 완료되었으나 payload가 없어 큐에 등록하지 못했습니다. (93번 메뉴에서 생성 필요)")
            
        time.sleep(1.5) # 메시지 읽을 시간
        st.rerun()

with c3:
    if st.button("⏸ 보류(hold)", use_container_width=True):
        set_workflow(pid, "hold", supplier_id=w.get("supplier_id") or None, note=note)
        audit(auth["user_id"], auth["role"], "HOLD", pid, note)
        st.warning("hold 처리 완료")
        st.rerun()
