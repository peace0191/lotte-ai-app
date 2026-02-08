from __future__ import annotations
import streamlit as st

def render():
    st.markdown("## 🎓 대치동 교육환경")
    
    st.markdown("<h3 style='color:#d4af37;'>🏫 대치동 교육환경 정보</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: rgba(26, 26, 46, 0.9); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 16px; padding: 40px; color: #fff; line-height: 2.2; margin-bottom:30px;">
            <p>• **대치초등학교** (대치SK뷰 도보 3분)</p>
            <p>• **대도초등학교** (대치아이파크 도보 5분)</p>
            <p>• **대청중학교** (남녀공학, 대치팰리스 도보 4분)</p>
            <p>• **단대부중학교** (대치SK뷰 도보 5분)</p>
            <p>• **숙명여자고등학교** (대치SK뷰 도보 6분)</p>
            <p>• **단대부고등학교** (대치아이파크 도보 5분)</p>
            <br>
            <h4 style="color: #d4af37; margin-bottom: 20px;">🏤 학원가 정보</h4>
            <p>• 대치동 학원가 메인 (도보 1분)</p>
            <p>• 대형 학원 밀집 지역</p>
            <p>• 안전한 통학로 확보</p>
            <p>• 한티역 세권 (삼환아르누보2)</p>
            <br>
            <h4 style="color: #d4af37; margin-bottom: 20px;">📍 단지별 학군 특징</h4>
            <p><span style="background:#4A90E2; color:white; padding:2px 8px; border-radius:4px; font-weight:bold; margin-right:8px;">1</span> <strong>래미안대치팰리스</strong> - 대장 아파트, 대청중 최근접</p>
            <p><span style="background:#4A90E2; color:white; padding:2px 8px; border-radius:4px; font-weight:bold; margin-right:8px;">2</span> <strong>대치SK뷰</strong> - 학원가 메인, 대치초 배정</p>
            <p><span style="background:#4A90E2; color:white; padding:2px 8px; border-radius:4px; font-weight:bold; margin-right:8px;">3</span> <strong>대치아이파크</strong> - 명문학군 도보권, 단대부고 인근</p>
            <p><span style="background:#4A90E2; color:white; padding:2px 8px; border-radius:4px; font-weight:bold; margin-right:8px;">4</span> <strong>대치은마아파트</strong> - 교육 중심 투자 1순위</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:15px; font-weight:bold; color:#d4af37; font-size:16px; border-bottom:1px solid rgba(212,175,55,0.2); padding-bottom:10px;'>🎯 교육환경 빠른 상담 (클릭 시 챗봇으로 연결)</div>", unsafe_allow_html=True)
    
    edu_examples = [
        "대치동 학원가와 가장 가까운 아파트는?",
        "대치초, 대도초 배정 단지는 어디인가요?",
        "대치동에서 유해시설 없는 조용한 단지 추천해주세요.",
        "밤늦게 귀가하는 자녀에게 안전한 아파트는?",
        "도보로 대치동 학원가 이용 가능한 매물 위주로 보여주세요.",
        "단대부중고 배정 가능한 전세 매물 있나요?"
    ]

    def go_chat_edu_with_q(q_text):
        st.session_state["main_menu_widget"] = "💬 AI 챗봇"
        st.session_state.menu_index = 3
        st.session_state.education_context = True
        st.session_state.chat_origin = "education"
        # Initial chat setup with the question
        st.session_state.chat = [{"role":"assistant","content":"안녕하세요! 교육 환경에 대해 궁금하신 점을 해결해 드릴게요."}]
        # We can't easily trigger the 'build_response' here without importing, 
        # but we can set a flag for chatbot to process it. 
        # For now, let's just jump and set the first message.
        st.session_state.chat.append({"role":"user", "content": q_text})
        st.rerun()

    cols = st.columns(2)
    for i, ex in enumerate(edu_examples):
        cols[i % 2].button(ex, key=f"edu_ex_{i}", use_container_width=True, on_click=go_chat_edu_with_q, args=(ex,))

    st.markdown("---")
    st.subheader("🚀 빠른 메뉴 이동 (목록가기)")

    def nav_to(label, idx, edu_ctx=False):
        st.session_state["main_menu_widget"] = label
        st.session_state.menu_index = idx
        st.session_state.education_context = edu_ctx
        if edu_ctx:
            st.session_state.chat_origin = "education"
            st.session_state.chat = [{"role":"assistant","content":"안녕하세요! 교육 환경에 대해 궁금하신 점을 해결해 드릴게요."}]
        st.rerun()

    nav_cols = st.columns(3)
    nav_cols[0].button("🏠 전체 매물 목록보기", use_container_width=True, type="primary", on_click=nav_to, args=("🏠 추천매물", 1))
    nav_cols[1].button("🎯 AI 저평가", use_container_width=True, type="primary", on_click=nav_to, args=("🎯 AI 저평가", 2))
    nav_cols[2].button("💬 AI 프리미엄 상담", use_container_width=True, type="primary", on_click=nav_to, args=("💬 AI 챗봇", 3, True))

