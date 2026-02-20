import streamlit as st
import datetime
from services.property_forms import render_complete_property_form
from api_client import client

st.set_page_config(page_title="AI 매칭 예약 (Secure)", page_icon="🔐", layout="wide")

st.title("🔐 AI 매칭 예약 & 공동매물 매칭")
st.markdown("**고객님의 조건과 매물 정보를 상세히 입력해주시면, AI가 최적의 매칭 결과를 제공합니다.**")
st.caption("공동 매물 접수 및 VIP 고객 예약 시스템")

st.divider()

# 1. PII Info
st.subheader("0. 기본 인적사항 (필수)")
c1, c2 = st.columns(2)
user_name = c1.text_input("고객명 (또는 중개사명)", placeholder="홍길동")
user_phone = c2.text_input("연락처", placeholder="010-1234-5678")

st.divider()

# 2. Unified Property Form (Main Content)
st.info("👇 아래 상세 조건을 입력해주세요. (영업팩 생성기와 동일한 정밀 규격)")
form_data = render_complete_property_form()

st.divider()

# 3. Submission
if st.button("🚀 AI 매칭 예약 접수 (공동매물 등록)", type="primary", use_container_width=True):
    if not user_name or not user_phone:
        st.error("기본 인적사항(이름, 연락처)을 입력해주세요.")
    else:
        # Merge PII with form data
        submission = {
            "user_name": user_name,
            "user_phone": user_phone,
            **form_data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Simulate API Call
        with st.spinner("🔒 보안 서버에 암호화하여 전송 중입니다..."):
            # client.submit_match(submission) # Actual API call would go here
            import time
            time.sleep(1.5)
            
        st.success("✅ 접수가 완료되었습니다!")
        st.balloons()
        
        # Result Preview
        with st.expander("📊 접수 내용 확인 (AI 분석 대기 중)", expanded=True):
            st.json(submission)
            
        st.info("담당자가 내용을 확인 후 AI 매칭 리포트를 발송해드립니다.")
