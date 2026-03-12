import streamlit as st
from services.matching_svc import matching_svc

st.set_page_config(page_title="CRM Dashboard", layout="wide")

st.title("📊 통합 CRM 대시보드")

total_leads = len(matching_svc.match_reservations)
vip_count = len([r for r in matching_svc.match_reservations if r["status"] == "VIP_HOT"])
warm_count = len([r for r in matching_svc.match_reservations if r["status"] == "ANALYZING"])

col1, col2, col3 = st.columns(3)

col1.metric("총 리드 수", total_leads)
col2.metric("VIP 리드 수", vip_count)
col3.metric("일반 리드 수", warm_count)

st.divider()

st.markdown("## 📋 리드 상세")

for r in matching_svc.match_reservations:
    with st.container(border=True):
        st.write("고객명:", r["conditions"]["user_name"])
        st.write("매칭 점수:", r["match_score"])
        st.write("상태:", r["status"])
