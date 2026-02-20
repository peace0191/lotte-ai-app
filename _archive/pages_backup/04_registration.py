st.divider()
st.subheader("📎 기존 기능(레거시) 보기")
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/registration.py", label="📎 (레거시) 등록 폼/로직", use_container_width=True)
with c2:
    st.page_link("pages/ai_pre_register_legacy.py", label="📎 (레거시) 사전등록", use_container_width=True)
