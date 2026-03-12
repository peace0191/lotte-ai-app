from __future__ import annotations

from pathlib import Path
import json
import time

import streamlit as st

from services.assets_store import ensure_property_tree, list_property_ids
from services.youtube_uploader import upload_video_from_payload
from services.auth_helper import require_role
from services.db import get_workflow, audit, publish_event, set_workflow

st.set_page_config(page_title="📤 YouTube 실제 업로드", layout="wide")
# 유튜브 업로드는 관리자만? 아니면 공급자도? 
# Step 7.5 says "auth = require_role('admin') # 유튜브 업로드는 관리자만"
auth = require_role("admin")

st.title("📤 YouTube 실제 업로드 (관리자 전용)")
st.caption("publish/youtube/upload_payload.json을 기반으로 실제 업로드를 실행합니다. Google OAuth 인증이 필요합니다.")

ids = list_property_ids()
if not ids:
    st.warning("매물이 없습니다.")
    st.stop()

# 가장 최근에 수정한 매물 선택
idx = len(ids) - 1
if "selected_property_id" in st.session_state and st.session_state.selected_property_id in ids:
    idx = ids.index(st.session_state.selected_property_id)

pid = st.selectbox("매물 선택", ids, index=idx)
st.session_state.selected_property_id = pid
paths = ensure_property_tree(pid)

# Workflow Check (Step 7.5 logic)
w = get_workflow(pid) or {}
status = w.get("status", "draft")
st.info(f"현재 상태: **{status}**")

if status != "approved":
    st.error(f"⚠️ 현재 상태가 approved가 아닙니다. 관리자 승인(95번 메뉴) 후 업로드 가능합니다.")
    st.stop()

payload_path = paths.publish_youtube / "upload_payload.json"

if not payload_path.exists():
    st.error("upload_payload.json이 없습니다. 93(광고 발행 센터)에서 payload를 먼저 생성하세요.")
    st.stop()

payload = json.loads(payload_path.read_text(encoding="utf-8"))

c1, c2 = st.columns([1, 1], vertical_alignment="top")
with c1:
    st.subheader("Payload 확인")
    st.json(payload)

with c2:
    st.subheader("실제 업로드 실행")
    st.warning("⚠ 최초 1회는 브라우저 인증이 뜹니다. (로컬 브라우저 팝업)")
    
    if st.button("🚀 YouTube 업로드 실행", use_container_width=True):
        with st.spinner("업로드 중... (파일 크기에 따라 수 분 소요 가능)"):
            try:
                res = upload_video_from_payload(payload_path)
                
                # 성공 처리
                st.success("업로드 완료 ✅")
                st.write(res)
                
                watch_url = res.get("watch_url", "")
                video_id = res.get("video_id", "")
                
                if watch_url:
                    st.markdown(f"▶ **영상 링크:** {watch_url}")
                    
                    # payload 업데이트
                    payload["uploaded_video_id"] = video_id
                    payload["uploaded_watch_url"] = watch_url
                    payload["uploaded_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                    
                    # 로그 및 상태 업데이트
                    publish_event(pid, "youtube", "ok", watch_url)
                    audit(auth["user_id"], auth["role"], "YOUTUBE_UPLOAD_OK", pid, watch_url)
                    set_workflow(pid, "published", supplier_id=w.get("supplier_id"))
                    
            except Exception as e:
                st.error(f"업로드 실패: {e}")
                publish_event(pid, "youtube", "fail", str(e))
                audit(auth["user_id"], auth["role"], "YOUTUBE_UPLOAD_FAIL", pid, str(e))
