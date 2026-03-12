import streamlit as st
from services.ga_helper import track_once, track

st.set_page_config(page_title="AI 챗봇", layout="wide")

track_once("view_page", {
    "page_name": "chatbot",
    "section": "consulting"
})

st.title("🟢 AI 상담 챗봇")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for role, msg in st.session_state["chat_history"]:
    with st.chat_message(role):
        st.markdown(msg)

prompt = st.chat_input("질문을 입력하세요")

if prompt:
    track("chat_message", {
        "message_length": len(prompt)
    })

    st.session_state["chat_history"].append(("user", prompt))
    answer = f"AI 답변 예시: {prompt} 관련 매물 추천 가능합니다."
    st.session_state["chat_history"].append(("assistant", answer))
    st.rerun()
