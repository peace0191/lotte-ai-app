import streamlit as st

def render(faq_common):
    # CSS Injection for Chat Input Visibility and Layout
    st.markdown("""
    <style>
    /* Chat Input Styling */
    div[data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        background-color: #222222 !important;
        caret-color: #d4af37 !important;
        font-weight: 500;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #888888 !important;
        opacity: 1;
    }
    /* Move Quick Nav to Top Visually if needed, but here we reorder in Python */
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div style="background:rgba(212, 175, 55, 0.05); border:1px solid rgba(212, 175, 55, 0.2); border-radius:15px; padding:20px; text-align:center; margin-bottom:20px;">
            <div style="font-size:24px; font-weight:900; color:#d4af37; margin-bottom:5px;">💬 AI Real Estate Assistant</div>
            <div style="font-size:13px; color:#9fa6b2;">전문 중개사와 AI가 함께 분석하는 초밀착 상담 시스템</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 1. Quick Navigation (Moved to Top)
    with st.expander("🎬 추천 서비스 바로가기 (단지별 매물 / AI 시그널)", expanded=False):
        nav_cols = st.columns(2)
        nav_cols[0].button("🏠 단지별 추천매물 보기", key="nav_home_top", 
                        on_click=lambda: (st.session_state.update({"redirect_to": "🏠 추천매물", "selected": None})))
        nav_cols[1].button("🎯 AI 매칭 시그널 보기", key="nav_uv_top", 
                        on_click=lambda: (st.session_state.update({"redirect_to": "🎯 AI 매칭 시그널", "selected": None})))

    # FAQ or Property Info
    if st.session_state.get("selected"):
        it = st.session_state.selected
        score = it.get("current_score", 0)
        score_color = "#00d1b2" if score >= 80 else "#d4af37" if score >= 60 else "#ff4b4b"
        
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:15px; margin-bottom:15px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="font-weight:800; color:#fff;">📍 상담 매물: {it.get('name', '매물')}</div>
                    <div style="background:{score_color}; color:#000; padding:2px 10px; border-radius:10px; font-size:11px; font-weight:800;">AI {score}점</div>
                </div>
                <div style="background:rgba(212,175,55,0.1); border:1px solid rgba(212,175,55,0.3); border-radius:8px; padding:10px;">
                    <div style="font-size:12px; color:#d4af37; font-weight:700;">🤝 실시간 매칭 실황</div>
                    <div style="display:flex; justify-content:space-between; margin-top:5px;">
                        <span style="font-size:11px; color:#adb5bd;">매칭 확률: <b style="color:#fff;">95%</b></span>
                        <span style="font-size:11px; color:#adb5bd;">대기 중인 매수자: <b style="color:#fff;">4명</b></span>
                    </div>
                    <div style="width:100%; background:rgba(255,255,255,0.1); height:4px; border-radius:2px; margin-top:8px;">
                        <div style="width:95%; background:#d4af37; height:4px; border-radius:2px;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Chat History
    if "chat" not in st.session_state:
        st.session_state.chat = [{"role": "assistant", "content": "안녕하세요! 대치1동 명품 매물에 대해 무엇을 도와드릴까요?"}]

    # Auto-responder for redirects or new messages
    from services.chat import build_response
    
    if st.session_state.chat[-1]["role"] == "user":
        with st.spinner("AI가 분석 중입니다..."):
            response = build_response(st.session_state.chat[-1]["content"], faq_common, st.session_state.get("selected"))
            st.session_state.chat.append({"role": "assistant", "content": response})

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # FAQ Section (Placed at Bottom)
    st.markdown("---")
    st.markdown("### 💡 자주 묻는 질문 (Top 50+)")
    from services.faq_data import FAQ_CATEGORIES
    
    faq_tabs = st.tabs(list(FAQ_CATEGORIES.keys()))
    
    # Callback to send message
    def send_faq(txt):
        st.session_state.chat.append({"role": "user", "content": txt})
        # Force rerun handles the rest in the main loop
        
    for i, (cat, questions) in enumerate(FAQ_CATEGORIES.items()):
        with faq_tabs[i]:
            # Use columns to create a grid-like layout for buttons
            q_cols = st.columns(2)
            for j, q in enumerate(questions):
                if q_cols[j % 2].button(q, key=f"faq_{i}_{j}", use_container_width=True):
                    send_faq(q)
                    st.rerun()

    # Footer / Contact (Moved to bottom of content, above input)
    st.markdown("""
        <div style="margin-top:30px; margin-bottom:80px; padding:20px; border-top:1px solid rgba(255,255,255,0.05); text-align:center;">
            <div style="font-size:12px; color:#6c757d; margin-bottom:5px;">상담 문의: 02-578-8285</div>
            <div style="font-size:11px; color:#444;">롯데타워앤강남빌딩부동산중개(주)</div>
        </div>
    """, unsafe_allow_html=True)

    # Chat Input (Always Fixed Bottom)
    prompt = st.chat_input("추가질문 기재하기")
    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})
        st.rerun()

    from services.ui import render_bottom_nav
    render_bottom_nav("💬 AI 챗봇")
