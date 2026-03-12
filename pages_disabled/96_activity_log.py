from __future__ import annotations

import streamlit as st

from services.auth_helper import require_role
from services.db import list_audit, list_publish, list_workflows

st.set_page_config(page_title="📊 운영 로그", layout="wide")
auth = require_role("admin")

st.title("📊 운영 로그/감사(Audit) 센터")
st.caption("누가/언제/어떤 행동을 했는지, 발행 성공/실패를 한 눈에 확인합니다.")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("워크플로우(최근)", len(list_workflows(200)))
with c2:
    st.metric("감사 로그(최근)", len(list_audit(300)))
with c3:
    st.metric("발행 로그(최근)", len(list_publish(200)))

st.divider()

tab1, tab2, tab3 = st.tabs(["워크플로우", "감사 로그", "발행 로그"])
with tab1:
    st.dataframe(list_workflows(200), use_container_width=True)
with tab2:
    st.dataframe(list_audit(300), use_container_width=True)
with tab3:
    st.dataframe(list_publish(200), use_container_width=True)
