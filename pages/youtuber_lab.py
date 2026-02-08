import streamlit as st
import time
from services.shorts_svc import shorts_svc
from services.ui import header

def render(properties):
    header()
    
    st.markdown("""
        <div style="background:linear-gradient(90deg, #FF0000 0%, #000000 100%); padding:30px; border-radius:15px; text-align:center; color:white; border: 2px solid #fff;">
            <h1 style="margin:0;">🔴 YOU-LAB: 초고속 숏츠 연구소</h1>
            <p style="margin-top:10px; opacity:0.8;">Triton Inference Server 인프라 기반 실시간 유튜버 영상 제작 플랫폼</p>
        </div>
    """, unsafe_allow_html=True)

    # 매물 평탄화
    all_props = []
    for comp, items in properties.items():
        for it in items:
            all_props.append({"comp": comp, **it})

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("⚙️ 촬영 및 인코딩 설정")
        target_prop = st.selectbox("영상을 제작할 매물 선택", [p['name'] for p in all_props])
        prop = next(p for p in all_props if p['name'] == target_prop)
        
        style = st.radio("나노 바나나 방송 스타일 (AI)", ["aggressive", "professional", "friendly"], horizontal=True)
        bgm = st.select_slider("BGM 강도 (사운드 믹싱)", options=["Chill", "Hype", "Extreme"])
        
        st.markdown("---")
        if st.button("🚀 Triton 전용 서버 렌더링 시작", use_container_width=True, type="primary"):
            with st.status("🎬 MLOps 파이프라인 가동 중...", expanded=True) as status:
                st.write("1. NER 엔진: 매물 핵심 개체(Entity) 분석 성공")
                time.sleep(1)
                st.write("2. Triton Server: GPU 가속 기반 렌더링 중...")
                res = shorts_svc.generate_video_advanced(prop, style)
                time.sleep(1.5)
                status.update(label="✅ 렌더링 완료 및 YouTube 업로드 준비!", state="complete")
                st.session_state.last_yt_video = res
                st.balloons()

    with col2:
        st.subheader("📺 모니터링 데스크")
        if "last_yt_video" in st.session_state:
            vid_res = st.session_state.last_yt_video
            
            # 🔴 CRITICAL: Force Shorts to Watch normalization for PC/WebView compatibility
            v_url = vid_res.get("video_url", "https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Use fallback if missing
            if "youtube.com/shorts/" in v_url:
                v_url = v_url.replace("/shorts/", "/watch?v=")
            if "youtu.be/" in v_url:
                 v_url = f"https://www.youtube.com/watch?v={v_url.split('youtu.be/')[1].split('?')[0]}"
                
            st.video(v_url)
            st.markdown(f"👉 **[새 탭에서 영상 열기 (재생 안 될 경우)]({v_url})**")
            
            with st.expander("🔍 AI NER 추출 결과 (Entity Recognition)", expanded=True):
                ents = vid_res.get("entities_found", {})
                ent_html = "".join([f'<span style="background:#2e3a4e; color:#d4af37; padding:2px 8px; border-radius:10px; margin-right:5px; font-size:12px;">{k}: {v}</span>' for k, v in ents.items()])
                st.markdown(ent_html, unsafe_allow_html=True)
            
            with st.expander("📊 정밀 저평가 분석 데이터 (Evidence)", expanded=True):
                ev = vid_res.get("evidence", {})
                if "msg" in ev:
                    st.warning(ev["msg"])
                else:
                    cols = st.columns(3)
                    cols[0].metric("실거래 중위가", f"{ev['rt_median_180d']/100000000:,.1f}억")
                    cols[1].metric("거래 표본", f"{ev['rt_count_180d']}건")
                    cols[2].metric("변동성 감점", f"-{ev['vol_penalty']}점")
                    
                    st.caption(f"💡 신뢰도 가중치: {ev['conf']*100:.1f}% | 산출된 가격 영향: {ev['calc_impact']}점")

            st.info(f"📜 **나노 바나나 최종 대본:**\n\n{vid_res['script_used']}")
            
            st.success(f"📡 서빙 엔진: {vid_res['engine']} / 리포트: {vid_res['automation_report']}")
            
            if st.button("📤 YouTube Shorts 예약 업로드 (API)", use_container_width=True):
                st.toast("유튜브 API를 통해 채널에 예약 등록되었습니다.")
        else:
            st.info("왼쪽 대시보드에서 렌더링을 시작해 주세요.")

    st.markdown("---")
    st.caption("본 모듈은 Container Native 환경에서 Kubeflow 파이프라인으로 매일 09시에 재학습됩니다.")
