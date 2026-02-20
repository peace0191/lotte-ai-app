import streamlit as st

st.divider()
st.subheader("📎 기존 기능(레거시) 보기")
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/education.py", label="📎 (레거시) 교육/학군 콘텐츠", use_container_width=True)
with c2:
    st.page_link("pages/dashboard.py", label="📎 (레거시) 대시보드/요약", use_container_width=True)
