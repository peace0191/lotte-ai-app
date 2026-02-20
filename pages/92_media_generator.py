from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import streamlit as st

from services.assets_store import ensure_property_tree, list_property_ids
from services.media_pipeline import run_all_generate, list_raw_photos, list_raw_videos
from services.auth_helper import require_role
from services.db import set_workflow, audit

st.set_page_config(page_title="🎬 자동 생성 센터", layout="wide")
auth = require_role("supplier", "admin")

st.title("🎬 자동 생성 센터")
st.caption("업로드된 raw 자료로 ‘숏츠 + 썸네일 + 카카오 카드 + 사진 워터마크본’을 한 번에 생성하고 바로 미리보기합니다.")

ids = list_property_ids()
if not ids:
    st.warning("매물이 없습니다. 먼저 ‘🧰 미디어 업로드 센터’에서 매물을 생성/업로드하세요.")
    st.stop()

# 가장 최근에 수정한 매물 선택 (session state)
idx = len(ids) - 1
if "selected_property_id" in st.session_state and st.session_state.selected_property_id in ids:
    idx = ids.index(st.session_state.selected_property_id)

pid = st.selectbox("매물 선택", ids, index=idx)
st.session_state.selected_property_id = pid
paths = ensure_property_tree(pid)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("사진(raw)", len(list_raw_photos(paths)))
with c2:
    st.metric("영상(raw)", len(list_raw_videos(paths)))
with c3:
    st.caption(f"폴더: `{paths.base.as_posix()}`")

if st.button("🚀 전체 자동 생성 실행", use_container_width=True):
    with st.spinner("생성 중... (사진→숏츠→썸네일/카카오 순서)"):
        res = run_all_generate(paths)
    if res.ok:
        st.success("생성 완료 ✅")
        set_workflow(pid, "generated", supplier_id=auth["user_id"])
        audit(auth["user_id"], auth["role"], "GENERATE_ALL_CENTER", pid, "ok")
    else:
        st.error("생성 중 일부 실패가 있습니다. 아래 로그를 확인하세요.")
    st.session_state["gen_messages"] = res.messages
    st.session_state["gen_created"] = res.created_files

st.divider()

# 로그
if "gen_messages" in st.session_state:
    with st.expander("📋 생성 로그 보기", expanded=True):
        for m in st.session_state["gen_messages"]:
            st.write(m)

# 결과 미리보기
st.subheader("🧾 생성 결과 미리보기")

left, right = st.columns([1, 1], vertical_alignment="top")

with left:
    st.markdown("### 🖼️ 썸네일/카카오 카드")
    thumbs = sorted(list(paths.processed_thumbs.glob("*.jpg")))
    if not thumbs:
        st.info("아직 생성된 썸네일/카카오 카드가 없습니다.")
    else:
        # 그리드
        tcols = st.columns(2)
        for i, p in enumerate(thumbs):
            with tcols[i % 2]:
                st.image(str(p), caption=p.name, use_container_width=True)

with right:
    st.markdown("### 🎞️ 숏츠 영상")
    vids = sorted(list(paths.processed_videos.glob("*.mp4")))
    if not vids:
        st.info("아직 생성된 숏츠 영상이 없습니다.")
    else:
        for p in vids:
            st.markdown(f"**{p.name}**")
            st.video(str(p))

st.divider()

st.markdown("### 🖼️ 사진 워터마크/리사이즈 결과(일부)")
processed_photos = sorted(list(paths.processed_photos.glob("*.jpg")))
if not processed_photos:
    st.info("아직 processed/photos 결과가 없습니다.")
else:
    cols = st.columns(4)
    for i, p in enumerate(processed_photos[:12]):
        with cols[i % 4]:
            st.image(str(p), caption=p.name, use_container_width=True)
