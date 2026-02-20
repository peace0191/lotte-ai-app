import streamlit as st
from services.matching_svc import matching_svc

st.set_page_config(page_title="Admin Center", layout="wide")

st.title("🛠 관리자 센터")

st.markdown("## 📊 실시간 리드 감지")

if matching_svc.match_reservations:
    latest = matching_svc.match_reservations[-1]

    if latest.get("status") == "VIP_HOT":
        st.warning(f"🔥 VIP 리드 발생: {latest['conditions'].get('user_name')}")
    else:
        st.info("최근 리드는 일반 리드입니다.")
else:
    st.info("아직 리드가 없습니다.")

st.divider()

st.markdown("## 📋 전체 리드 리스트")

for r in matching_svc.match_reservations:
    with st.container(border=True):
        st.write("고객:", r["conditions"]["user_name"])
        st.write("점수:", r["match_score"])
        st.write("상태:", r["status"])
