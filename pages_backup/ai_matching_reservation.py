
import streamlit as st
import datetime
from services.matching_svc import matching_svc
from api_client import client  # ✅ Secure API Client Import
from services.survey_questions import SURVEY_SECTIONS, get_survey_metadata

st.set_page_config(page_title="VIP 매칭 진단 (Secure)", page_icon="🔐", layout="wide")

meta = get_survey_metadata()
st.title(f"📝 {meta['title']}")
st.markdown(f"**{meta['desc']}**")

# API Status Indicator
api_status = "🔴 Disconnected"
try:
    health = client.check_health()
    if health and health.get("status") == "ok":
        api_status = "🟢 Secure API Connected"
except:
    pass
st.caption(f"시스템 상태: {api_status}")

st.divider()

# ------------------------------------------------------------------------------
# 1. PII & Basic Contact Info (필수)
# ------------------------------------------------------------------------------
st.markdown("### 📞 연락처 정보 (필수)")
col_pii1, col_pii2 = st.columns(2)
with col_pii1:
    user_name = st.text_input("고객명 (성함)", placeholder="예: 홍길동")
with col_pii2:
    user_phone = st.text_input("연락처 (핸드폰)", placeholder="예: 010-1234-5678")

st.info("💡 입력하신 정보는 은행급 보안 등급의 안전한 서버에 저장됩니다.")

# ------------------------------------------------------------------------------
# 2. Detailed Survey (50 Questions)
# ------------------------------------------------------------------------------
st.markdown("---")
responses = {}

with st.form("vip_survey_form"):
    
    # Loop through sections
    for section_name, questions in SURVEY_SECTIONS.items():
        with st.expander(section_name, expanded=True):
            for q in questions:
                # 위젯 키는 q['id'] 사용
                qid = q['id']
                label = f"{q['q']}"
                # Add description if exists
                help_text = q.get('desc', None)
                
                # Render based on type
                q_type = q.get('type', 'text')
                
                if q_type == 'radio':
                    responses[qid] = st.radio(label, q['opts'], horizontal=True, help=help_text)
                elif q_type == 'select':
                    responses[qid] = st.selectbox(label, q['opts'], help=help_text)
                elif q_type == 'multiselect':
                    responses[qid] = st.multiselect(label, q['opts'], help=help_text)
                elif q_type == 'slider':
                    min_v = q.get('min', 1)
                    max_v = q.get('max', 5)
                    responses[qid] = st.slider(label, min_v, max_v, (min_v+max_v)//2, help=help_text)
                elif q_type == 'date':
                    responses[qid] = st.date_input(label, value=None, help=help_text)
                elif q_type == 'text_area':
                    responses[qid] = st.text_area(label, help=help_text)
                elif q_type == 'checkbox':
                    responses[qid] = st.checkbox(label, help=help_text)
                else: # text default
                    placeholder = q.get('placeholder', '')
                    responses[qid] = st.text_input(label, placeholder=placeholder, help=help_text)
            
            st.write("") # Spacer

    submit_btn = st.form_submit_button("✅ VIP 정밀 진단 제출 (Secure Save)", use_container_width=True, type="primary")

# ------------------------------------------------------------------------------
# 3. Submission Logic (Hybrid: Secure API + Local Logic)
# ------------------------------------------------------------------------------
if submit_btn:
    # Essential Check
    if not user_name or not user_phone:
        st.error("고객명과 연락처는 필수 입력 항목입니다.")
        st.stop()
        
    # Prepare Conditions
    deal_type_map = responses.get("q26", "매매")
    if "전세" in str(deal_type_map): deal_type = "전세"
    elif "월세" in str(deal_type_map): deal_type = "월세"
    else: deal_type = "매매"
    
    move_in = str(responses.get("q46", ""))
    
    conditions = {
        "user_name": user_name,
        "user_phone": user_phone,
        "district": "대치동",
        "type": deal_type,
        "move_in_date": move_in,
        "survey_data": responses
    }

    # 1️⃣ Secure API Save (Priority)
    api_success = False
    with st.spinner("💾 안전한 보안 서버에 데이터를 저장 중입니다..."):
        try:
            # api_client.py의 새 메서드 호출
            res = client.submit_vip_survey(user_name, user_phone, responses)
            if res and res.get("ok"):
                api_success = True
                st.toast("✅ 보안 서버 저장 완료!")
            else:
                st.toast("⚠️ 서버 연결 실패. 로컬 모드로 전환합니다.")
        except Exception as e:
            st.error(f"API Error: {e}")

    # 2️⃣ Local Matching Logic (Immediately Feedback)
    # API가 데이터를 저장만 하고 계산 로직이 없다면, 로컬 서비스로 계산해서 보여줌
    try:
        # Register to local memory for instant calc (Demo fallback)
        result = matching_svc.register_match_request(
            user_id=user_name,
            conditions=conditions
        )
        
        st.success("✅ VIP 정밀 진단이 완료되었습니다.")
        
        # Extract Result
        score = result.get("match_score", 0)
        advice = result.get("advice", "")
        alerts = result.get("alerts", [])
        
        # Result Card
        st.divider()
        st.markdown(f"### 📊 AI 매칭 분석 결과: {score}점")
        
        col_res1, col_res2 = st.columns([1, 2])
        with col_res1:
            if score >= 80:
                st.markdown("## 🔥 VIP_HOT")
                st.caption("즉시 매칭 최우선 순위")
            elif score >= 50:
                 st.markdown("## 🟢 WARM")
                 st.caption("적합 매물 탐색 중")
            else:
                 st.markdown("## ⚪ GENERAL")
                 st.caption("조건 모니터링 대기")
                 
        with col_res2:
            if advice:
                st.info(f"💡 조언: {advice}")
            if alerts:
                for a in alerts:
                    st.write(a)
        
        if api_success:
            st.code(f"Server Transaction ID: {res.get('id')} (Securely Stored)", language="text")
        else:
            st.warning("⚠️ 현재 로컬 데모 모드입니다. 데이터가 서버에 영구 저장되지 않았을 수 있습니다.")
            
    except Exception as e:
        st.error(f"제출 중 오류가 발생했습니다: {e}")
