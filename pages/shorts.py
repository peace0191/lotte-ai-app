import streamlit as st
from pathlib import Path
import shutil
import time
from services.video_renderer import render_premium_shorts, has_ffmpeg
from services.sales_templates import generate_pack
from gtts import gTTS

FALLBACK_MP4 = str(Path("assets") / "fallback.mp4")
# ... (rest of imports/constants)

# ... (rest of imports/constants)


def _find_bgm() -> str | None:
    candidates = [
        Path("assets/bgm/lounge.mp3"),
        Path("assets/lounge.mp3"),
        Path("bgm/lounge.mp3"),
        Path("assets/bgm.mp3"),
        Path("services/assets/bgm/lounge.mp3") 
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

def get_selected_property():
    p = st.session_state.get("selected_property")
    if not p:
        st.warning("선택된 매물이 없습니다. 메인 목록에서 매물을 선택해주세요.")
        if st.button("🏠 메인 목록으로"):
            st.session_state["redirect_to"] = "🏠 추천매물"
            st.rerun()
        st.stop()
    return p

# 🔑 선택된 매물 가져오기
p = get_selected_property()

title = p.get("title","")
section = p.get("section","")
price = p.get("price","")
area = p.get("area_py","")
deal_type = "매매" # Default or extract
if "전세" in str(price): deal_type = "전세"
elif "월세" in str(price): deal_type = "월세"
video_url = (p.get("video_url") or "").strip()

# UI 헤더
st.markdown(f"### 🏙️ {section}")
st.markdown(f"## 🎬 '{title}' 전용 홍보 영상 생성기")
st.caption(f"면적: {area}평 | 가격: {price}")

# 좌: 영상 / 우: 상태
left, right = st.columns([1.2, 1], gap="large")

with left:
    if video_url:
        # Force Shorts -> Watch normalization
        if "youtube.com/shorts/" in video_url:
            video_url = video_url.replace("/shorts/", "/watch?v=")
        if "youtu.be/" in video_url:
            video_url = f"https://www.youtube.com/watch?v={video_url.split('youtu.be/')[1].split('?')[0]}"
             
        st.video(video_url)
        st.caption(f"📌 현재 재생 중: {title} 관련 영상")
        # Fallback Link
        st.markdown(f"👉 **[새 탭에서 영상 열기 (재생 안 될 경우)]({video_url})**")
    else:
        st.info("등록된 영상이 없어 기본 브리핑 영상으로 대체합니다.")
        if Path(FALLBACK_MP4).exists():
            st.video(FALLBACK_MP4)
        else:
            # st.warning("assets/fallback.mp4 가 없어 영상 미리보기를 표시할 수 없습니다.")
            # Use placeholder
            st.empty()

with right:
    st.markdown("### ✨ AI 분석 & 자동화 현황")
    status = st.session_state.get("ai_video_status", "idle")  # idle/processing/done/error
    
    if status == "idle":
        st.write("대기 중…")
    elif status == "processing":
        st.warning("생성 중… 잠시만요")
    elif status == "done":
        st.success("생성 완료 ✅")
    elif status == "error":
        st.error(f"생성 실패 ❌: {st.session_state.get('video_error','')}")

    st.divider()
    st.write("**마케팅 톤**: 실거래 근거 기반 ‘정밀 브리핑’")
    st.write("**BGM 구성**: 프리미엄 럭셔리 라운지")
    
    # Checkbox features (Mock)
    st.checkbox("실거래가 자동 반영", value=True, disabled=True)
    st.checkbox("네이버 부동산 연동", value=True, disabled=True)

# 실행 버튼
st.divider()

if st.button("🚀 실시간 AI 영상 제작 시작", use_container_width=True, type="primary"):
    st.session_state["ai_video_status"] = "processing"
    # Need to rerun to show processing state immediately
    st.rerun()

# Processing Logic
if status == "processing":
    with st.spinner("AI가 매물 정보를 분석하고 영상을 구성 중입니다..."):
        # Real generation logic
        # out_path = f"outputs/videos/{p.get('id','temp')}_briefing.mp4"
        
        # --- Safe Path Logic ---
        import tempfile
        ROOT = Path(__file__).resolve().parents[1]  # pages/shorts.py -> project root
        SAFE_BASE = ROOT / "outputs" / "videos"

        def _safe_out_path(property_id: str) -> str:
            try:
                SAFE_BASE.mkdir(parents=True, exist_ok=True)
                # Test write
                test = SAFE_BASE / "__write_test__.tmp"
                test.write_text("ok", encoding="utf-8")
                test.unlink(missing_ok=True)
                return str(SAFE_BASE / f"{property_id}_briefing.mp4")
            except Exception as e:
                print(f"Write permission error on {SAFE_BASE}: {e}")
                # Fallback to temp
                tmpdir = Path(tempfile.gettempdir()) / "lotte_ai_outputs"
                tmpdir.mkdir(parents=True, exist_ok=True)
                return str(tmpdir / f"{property_id}_briefing.mp4")

        out_path = _safe_out_path(str(p.get('id', 'temp')))
        # -----------------------
        
        # Prepare params
        try:
            # Render video
            if has_ffmpeg():
                # Option 1: Premium Shorts Mode (9:16) + TTS + SlideShow
                # Script Construction
                tags_str = p.get('tags', [''])[0] if isinstance(p.get('tags'),list) and p.get('tags') else '추천'
                script = f"{p.get('complex_name', title)} {area}평형 매물입니다. 가격은 {price}이며, {tags_str} 매물입니다. 지금 바로 문의주세요."
                
                # Audio Generation (TTS) - Non-blocking
                tts_path = Path("outputs/tts") / f"{p.get('id', 'temp')}.mp3"
                tts_path.parent.mkdir(parents=True, exist_ok=True)
                
                narration_mp3 = None
                try:
                    tts = gTTS(text=script, lang='ko', slow=False)
                    tts.save(str(tts_path))
                    narration_mp3 = str(tts_path)
                except Exception as tts_err:
                    print(f"TTS Error (continuing without narration): {tts_err}")
                    st.warning(f"TTS 생성 실패(무시하고 진행): {tts_err}")
                    narration_mp3 = None # Continue without TTS

                # Image Collection
                image_dir = Path("images") / str(p.get("id", "temp"))
                
                # BGM Path Handling (Robust)
                bgm_path = _find_bgm() # Returns None if not found

                result_path = render_premium_shorts(
                    property_id=p.get('id', 'temp'),
                    title=title,
                    price=price,
                    area=str(area),
                    tags=p.get("tags", []),
                    images_dir=str(image_dir),
                    narration_mp3=narration_mp3,
                    bgm_mp3=bgm_path,
                    out_path=out_path,
                    size=(720,1280),
                    per_image_sec=2.4,
                    crossfade=0.35
                )
                
                st.session_state["video_result_path"] = result_path
                st.session_state["ai_video_status"] = "done"
            else:
                # Fallback
                st.warning("FFmpeg가 설치되지 않아 기본 영상을 재생합니다.")
                time.sleep(1.5) # Simulate work
                st.session_state["video_result_path"] = FALLBACK_MP4 if Path(FALLBACK_MP4).exists() else ""
                st.session_state["ai_video_status"] = "done"
                
        except ImportError as ie:
             st.session_state["ai_video_status"] = "error"
             st.session_state["video_error"] = f"라이브러리 누락: {ie}"
        except Exception as e:
            st.session_state["ai_video_status"] = "error"
            st.session_state["video_error"] = f"영상 생성 중 오류: {e}"
            
    st.rerun()

# Result Display
if st.session_state.get("ai_video_status") == "done":
    st.success("🎉 AI 영상 및 영업팩 생성이 완료되었습니다!")

    if "upload_result" in st.session_state:
        res = st.session_state["upload_result"]
        st.markdown(f"""
        <div style="background:rgba(0, 200, 83, 0.1); border:1px solid #00c853; padding:15px; border-radius:10px; margin-bottom:20px;">
            <h4 style="color:#00c853; margin:0;">🚀 자동 업로드 시뮬레이션 성공 ({res['platform']})</h4>
            <p style="margin:5px 0;">ID: {res.get('video_id', 'NV-Verify')}</p>
            <a href="{res['manual_url']}" target="_blank" style="background:#00c853; color:white; padding:5px 10px; text-decoration:none; border-radius:5px; font-size:12px;">📤 {res['platform']} 업로드 페이지 열기 (Manual)</a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## ✅ 생성 결과")
    r_col1, r_col2 = st.columns([1, 1])
    
    out_video = st.session_state.get("video_result_path","")
    with r_col1:
        st.markdown("#### 🎥 생성된 브리핑 영상")
        if out_video and Path(out_video).exists():
            st.video(out_video)
        else:
            st.info("결과 영상 파일이 없습니다.")
            
    with r_col2:
        st.markdown("#### 🏢 영업팩 (자동 생성)")
        
        # Generate Sales Pack
        sales_data = {
            "complex_name": section,
            "area": f"{area}평",
            "deal_type": deal_type,
            "highlight1": p.get("tags",[""])[0] if p.get("tags") else "",
            "highlight2": "AI추천",
            "highlight3": "급매",
            "tone": "표준",
            "main_video": video_url,
            "backup_video": "",
            "contact_name": "홍길동",
            "contact_tel": "010-1234-5678",
            "ai_score": "92", # Mock
            "ai_summary": p.get("description", "")
        }
        pack = generate_pack(sales_data)
        
        tab1, tab2, tab3 = st.tabs(["🎬 숏폼 대본", "🧾 네이버 문구", "📱 쇼룸"])
        
        with tab1:
            st.text_area("스크립트", pack["shorts_script"], height=150)
        with tab2:
            st.text_area("매물설명", pack["naver_copy"], height=150)
        with tab3:
             st.download_button(
                "⬇️ HTML 다운로드",
                data=pack["showroom_html"].encode("utf-8"),
                file_name=f"showroom_{p.get('id')}.html",
                mime="text/html",
                use_container_width=True
            )
    
    st.divider()
    st.markdown("### 📤 원클릭 자동 업로드 (Simulated)")
    u1, u2 = st.columns(2)
    
    from services.video_uploader import simulate_youtube_upload, simulate_naver_upload
    
    with u1:
        if st.button("🔴 YouTube Shorts 업로드", use_container_width=True):
             with st.spinner("YouTube API 연결 및 업로드 중..."):
                 res = simulate_youtube_upload(out_video, title, pack["shorts_script"], p.get("tags", []))
                 st.session_state["upload_result"] = res
                 st.toast("YouTube 업로드 완료!")
                 time.sleep(1)
                 st.rerun()
                 
    with u2:
        if st.button("🟢 네이버 부동산 영상등록", use_container_width=True):
            with st.spinner("네이버 매물광고센터 연결 중..."):
                res = simulate_naver_upload(out_video, p.get("id"), pack["naver_copy"])
                st.session_state["upload_result"] = res
                st.toast("네이버 업로드 승인 요청 완료!")
                time.sleep(1)
                st.rerun()

    if st.button("🏠 메인으로 돌아가기"):
        st.session_state["redirect_to"] = "🏠 추천매물"
        st.rerun()
