st.divider()
st.subheader("📎 기존 기능(레거시) 보기")
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/properties.py", label="📎 (레거시) 매물 목록/상세", use_container_width=True)
with c2:
    st.page_link("pages/undervalued.py", label="📎 (레거시) 저평가/급매 추천", use_container_width=True)
