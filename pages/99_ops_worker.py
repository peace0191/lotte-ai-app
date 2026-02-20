from __future__ import annotations

import streamlit as st

from services.auth_helper import require_role
from services.publish_queue import list_queue, fetch_due_jobs, mark_running, mark_done, mark_failed

st.set_page_config(page_title="🔧 운영 워커 (Test)", layout="wide")
auth = require_role("admin")

st.title("🔧 운영 워커 (Test Agent)")
st.caption("백그라운드에서 돌아야 할 워커(Worker)를 수동 테스트합니다.")

c1, c2 = st.columns(2)
with c1:
    st.markdown("### 📌 대기 중인 작업 (Queue)")
    jobs = list_queue(limit=20)
    if not jobs:
        st.info("대기 작업 없음")
    else:
        st.dataframe(jobs)

with c2:
    st.markdown("### ⚙️ 작업 실행 (1회)")
    if st.button("▶️ 작업 1개 가져와서 실행 (Fetch & Run)", use_container_width=True):
        due = fetch_due_jobs(limit=1)
        if not due:
            st.warning("실행할 작업이 없습니다 (Due date 미도래 또는 큐 비었음)")
        else:
            job = due[0]
            st.info(f"작업 시작: ID {job['id']} / {job['property_id']} ({job['channel']}) / Priority: {job['priority']}")
            
            # 실제 실행 로직 (scripts/ops_worker_once.py와 동일하게)
            try:
                import sys
                from pathlib import Path
                # Ensure scripts can be imported if not in path
                sys.path.append(str(Path(__file__).parent.parent))
                from scripts.ops_worker_once import process_job
                
                process_job(job)
                st.success(f"작업 완료: ID {job['id']}")
                st.rerun()
            except Exception as e:
                st.error(f"작업 실패: {e}")
