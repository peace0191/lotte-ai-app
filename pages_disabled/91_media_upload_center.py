from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

from services.assets_store import (
    ensure_property_tree,
    generate_new_property_id,
    list_property_ids,
    read_meta,
    safe_filename,
    save_uploaded_bytes,
    write_meta,
)
from services.db import set_workflow, audit
from services.auth_helper import require_role
from services.media_pipeline import (
    process_photos_watermark_and_resize,
    render_shorts_video,
    create_thumbnails,
    run_all_generate,
)

# ---- 설정 ----
MAX_PHOTOS = 19
MIN_VIDEO_SECONDS = 15

# 권한 체크 (공급자 또는 관리자)
auth = require_role("supplier", "admin")

st.set_page_config(page_title="🧰 미디어 업로드 센터", layout="wide")

# ---- 유틸: 영상 길이 검수 ----
def get_video_duration_seconds(video_path: Path) -> Optional[float]:
    try:
        from moviepy.editor import VideoFileClip  # type: ignore
        with VideoFileClip(str(video_path)) as clip:
            return float(clip.duration) if clip.duration is not None else None
    except Exception:
        return None  # moviepy 없거나 에러 시 패스

def human_sec(sec: Optional[float]) -> str:
    if sec is None:
        return "알 수 없음"
    m = int(sec // 60)
    s = int(sec % 60)
    if m <= 0:
        return f"{s}초"
    return f"{m}분 {s}초"


# ---- UI helpers ----
def section_title(title: str, desc: str = ""):
    st.markdown(
        f"""
        <div style="padding:.65rem .9rem;border-radius:.9rem;border:1px solid rgba(255,255,255,.12);
                    background:rgba(255,255,255,.03);margin:.4rem 0 1rem 0;">
          <div style="font-weight:800;font-size:1.05rem">{title}</div>
          <div style="opacity:.8;margin-top:.2rem">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def list_files(folder: Path, exts: Optional[Tuple[str, ...]] = None) -> List[Path]:
    if not folder.exists():
        return []
    files = [p for p in folder.iterdir() if p.is_file()]
    if exts:
        files = [p for p in files if p.suffix.lower() in exts]
    return sorted(files, key=lambda p: p.name.lower())


# ---- 상태 ----
if "selected_property_id" not in st.session_state:
    st.session_state.selected_property_id = None

if "last_saved_notice" not in st.session_state:
    st.session_state.last_saved_notice = ""


# ---- 페이지 헤더 ----
st.title("🧰 미디어 업로드 센터")
st.caption(
    "사진(최대 19장) + 영상(최소 15초) 업로드 → 자동 분류 저장(raw) → 미리보기까지. "
    "원클릭 전체 자동 생성으로 바로 이어집니다."
)

# ---- 1) 매물 선택/생성 ----
section_title("1) 매물 선택 / 신규 생성", "property_id 기준으로 자산이 자동 정리됩니다. (예: P2026_000183)")

col_a, col_b, col_c = st.columns([2, 1, 2], vertical_alignment="bottom")

with col_a:
    existing = list_property_ids()
    options = ["(신규 생성)"] + existing
    default_idx = 0
    if st.session_state.selected_property_id in existing:
        default_idx = options.index(st.session_state.selected_property_id)

    selected = st.selectbox("매물 선택", options, index=default_idx)

with col_b:
    if st.button("➕ 신규 매물 생성", use_container_width=True):
        new_id = generate_new_property_id()
        st.session_state.selected_property_id = new_id
        ensure_property_tree(new_id)
        
        # 워크플로우 초기화
        set_workflow(new_id, "draft", supplier_id=auth["user_id"], note="신규 생성됨")
        audit(auth["user_id"], auth["role"], "CREATE_PROPERTY", new_id, "신규 생성")
        
        st.success(f"신규 매물 생성됨: {new_id}")
        st.rerun()

with col_c:
    if selected != "(신규 생성)":
        st.session_state.selected_property_id = selected
    elif st.session_state.selected_property_id is None:
        pass # 선택 대기

property_id = st.session_state.selected_property_id
if not property_id:
    st.info("매물을 선택하거나 신규 생성해주세요.")
    st.stop()

paths = ensure_property_tree(property_id)

st.info(f"현재 선택된 매물: **{property_id}**  |  저장 경로: `{paths.base.as_posix()}`")

# ---- 2) meta.json 입력(최소) ----
section_title("2) 매물 기본 정보(meta.json)", "제목/주소/가격/면적/저평가율(%) 정도만 우선 저장합니다.")

meta = read_meta(paths)
mcol1, mcol2, mcol3, mcol4 = st.columns([2, 2, 1, 1])
with mcol1:
    title = st.text_input("매물 제목", value=meta.get("title", ""))
with mcol2:
    address = st.text_input("주소", value=meta.get("address", ""))
with mcol3:
    price = st.text_input("가격(숫자)", value=str(meta.get("price", "")))
with mcol4:
    area = st.text_input("전용면적(㎡)", value=str(meta.get("area", "")))

mcol5, mcol6, mcol7 = st.columns([1, 2, 2])
with mcol5:
    gap = st.text_input("저평가율(%)", value=str(meta.get("market_gap_percent", "")))
with mcol6:
    reservation_link = st.text_input("예약 링크(선택)", value=meta.get("reservation_link", ""))
with mcol7:
    status_val = st.selectbox("상태", ["active", "hold", "sold", "draft"], 
                              index=["active", "hold", "sold", "draft"].index(meta.get("status", "active")))

if st.button("💾 기본 정보 저장(meta.json)", use_container_width=True):
    write_meta(
        paths,
        {
            "property_id": property_id,
            "title": title,
            "address": address,
            "price": price,
            "area": area,
            "market_gap_percent": gap,
            "reservation_link": reservation_link,
            "status": status_val,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    st.session_state.last_saved_notice = f"저장 완료: {time.strftime('%H:%M:%S')}"
    st.success(st.session_state.last_saved_notice)

# ---- 3) 업로드 섹션 ----
section_title(
    "3) 사진/영상 업로드",
    f"사진은 최대 {MAX_PHOTOS}장 권장. 영상은 최소 {MIN_VIDEO_SECONDS}초 이상 권장(15~45초). 업로드 즉시 raw 폴더에 저장됩니다.",
)

up_col1, up_col2 = st.columns(2, vertical_alignment="top")

with up_col1:
    st.subheader("🖼️ 사진 업로드 (최대 19장)")
    photo_files = st.file_uploader(
        "사진을 드래그앤드롭(여러 장 가능)",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key=f"photos_{property_id}",
    )

    existing_photos = list_files(paths.raw_photos, exts=(".jpg", ".jpeg", ".png", ".webp"))
    st.caption(f"현재 저장된 사진: **{len(existing_photos)}장**")

    if photo_files:
        if len(existing_photos) + len(photo_files) > MAX_PHOTOS:
            st.error(f"사진 제한 초과: {len(existing_photos)+len(photo_files)}장 > {MAX_PHOTOS}장")
        else:
            saved = 0
            for uf in photo_files:
                fname = safe_filename(uf.name)
                dst = paths.raw_photos / fname
                data = uf.getvalue()
                save_uploaded_bytes(dst, data, overwrite=False)
                saved += 1
            
            # 워크플로우 업데이트
            set_workflow(property_id, "uploaded", supplier_id=auth["user_id"], note="사진 업로드됨")
            audit(auth["user_id"], auth["role"], "UPLOAD_PHOTOS", property_id, f"{saved}장 저장")
            
            st.success(f"사진 {saved}장 저장 완료")
            st.rerun()

with up_col2:
    st.subheader("🎞️ 영상 업로드 (최소 15초 이상)")
    video_files = st.file_uploader(
        "영상 업로드(여러 개 가능)",
        type=["mp4", "mov", "m4v", "avi", "mkv"],
        accept_multiple_files=True,
        key=f"videos_{property_id}",
    )

    existing_videos = list_files(paths.raw_videos, exts=(".mp4", ".mov", ".m4v", ".avi", ".mkv"))
    st.caption(f"현재 저장된 영상: **{len(existing_videos)}개**")

    if video_files:
        saved = 0
        rejected = 0
        for uf in video_files:
            fname = safe_filename(uf.name)
            dst = paths.raw_videos / fname
            data = uf.getvalue()
            saved_path = save_uploaded_bytes(dst, data, overwrite=False)

            dur = get_video_duration_seconds(saved_path)
            if dur is not None and dur < MIN_VIDEO_SECONDS:
                rejected += 1
                st.warning(f"길이 미달 경고: {saved_path.name} ({human_sec(dur)}) < {MIN_VIDEO_SECONDS}초")
            else:
                saved += 1

        # 워크플로우
        set_workflow(property_id, "uploaded", supplier_id=auth["user_id"], note="영상 업로드됨")
        audit(auth["user_id"], auth["role"], "UPLOAD_VIDEOS", property_id, f"저장{saved}, 경고{rejected}")

        st.success(f"영상 업로드 완료 (통과 {saved}/경고 {rejected})")
        st.rerun()

# ---- 4) 미리보기 ----
section_title("4) 미리보기", "업로드한 raw 파일을 즉시 확인합니다.")

prev_col1, prev_col2 = st.columns(2, vertical_alignment="top")

with prev_col1:
    st.subheader("🖼️ 사진 미리보기")
    photos = list_files(paths.raw_photos, exts=(".jpg", ".jpeg", ".png", ".webp"))
    if not photos:
        st.info("사진 없음")
    else:
        # 3열
        cols = st.columns(3)
        for i, p in enumerate(photos):
            with cols[i % 3]:
                st.image(str(p), caption=p.name, use_container_width=True)

with prev_col2:
    st.subheader("🎞️ 영상 미리보기")
    videos = list_files(paths.raw_videos, exts=(".mp4", ".mov", ".m4v", ".avi", ".mkv"))
    if not videos:
        st.info("영상 없음")
    else:
        st.caption(f"총 {len(videos)}개 (최근 2개)")
        for p in videos[-2:]:
            dur = get_video_duration_seconds(p)
            st.markdown(f"**{p.name}** ({human_sec(dur)})")
            st.video(str(p))

# ---- 5) 자동 생성(실행) ----
section_title("5) 자동 생성(실행)", "원클릭으로 숏츠/카카오/썸네일까지 생성합니다. 결과물은 processed/ 폴더에 저장됩니다.")

gen_col1, gen_col2, gen_col3 = st.columns(3)

with gen_col1:
    if st.button("🎬 숏츠 자동 생성", use_container_width=True):
        with st.spinner("숏츠 생성 중..."):
            res = render_shorts_video(paths)
        for m in res.messages:
            st.write(m)
        if res.ok:
            st.success("숏츠 생성 완료 ✅")
            set_workflow(property_id, "generated", supplier_id=auth["user_id"])
            audit(auth["user_id"], auth["role"], "GENERATE_SHORTS", property_id, "ok")
        else:
            st.error("생성 실패/경고")

with gen_col2:
    if st.button("🟡 카카오/썸네일 생성", use_container_width=True):
        with st.spinner("카카오/썸네일 생성 중..."):
            res = create_thumbnails(paths)
        for m in res.messages:
            st.write(m)
        if res.ok:
            st.success("카카오/썸네일 생성 완료 ✅")
            set_workflow(property_id, "generated", supplier_id=auth["user_id"])
            audit(auth["user_id"], auth["role"], "GENERATE_THUMBS", property_id, "ok")
        else:
            st.error("생성 실패/경고")

with gen_col3:
    if st.button("🚀 전체 자동 생성(추천)", use_container_width=True):
        with st.spinner("전체 자동 생성 중... (사진→숏츠→썸네일/카카오)"):
            res = run_all_generate(paths)
        for m in res.messages:
            st.write(m)
        if res.ok:
            st.success("전체 자동 생성 완료 ✅")
            set_workflow(property_id, "generated", supplier_id=auth["user_id"])
            audit(auth["user_id"], auth["role"], "GENERATE_ALL", property_id, "ok")
        else:
            st.error("일부 실패/경고 로그 확인")

st.divider()
st.caption("✅ 업로드 센터 완료. 다음 단계에서 `92_media_generator.py`를 통해 결과를 모아서 보거나 `93_publish_center.py`로 발행 준비를 합니다.")
