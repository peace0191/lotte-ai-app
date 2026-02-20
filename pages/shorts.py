import streamlit as st
from services.video_renderer import render_premium_shorts
from services.shorts_svc import generate_shorts_script

st.title("🎥 숏츠 생성")

title = st.text_input("제목")
if st.button("스크립트 생성"):
    script = generate_shorts_script(title)
    st.text_area("스크립트", script)

if st.button("영상 생성"):
    render_premium_shorts(title=title)
    st.success("숏츠 생성 완료")
