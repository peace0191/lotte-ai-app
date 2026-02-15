st.divider()
st.subheader("📎 기존 기능(레거시) 보기")
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/ai_matching_reservation.py", label="📎 (레거시) 예약/매칭 화면", use_container_width=True)
with c2:
    st.page_link("pages/chatbot.py", label="📎 (레거시) AI 챗봇", use_container_width=True)
