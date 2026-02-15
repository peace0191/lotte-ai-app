st.divider()
st.subheader("📎 기존 기능(레거시) 보기")
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/shorts.py", label="📎 (레거시) 숏츠 생성", use_container_width=True)
with c2:
    st.page_link("pages/youtuber_lab.py", label="📎 (레거시) YOU-LAB", use_container_width=True)
