import streamlit as st
from services.property_forms import render_complete_property_form

st.set_page_config(page_title="AI 사전등록 (매칭)", page_icon="📝", layout="wide")

st.title("📝 AI 사전등록 (매물/고객)")
st.caption("AI 에이전트가 고객님의 조건을 기억하고, 적합한 매물/고객이 나타나면 즉시 알림을 드립니다.")

st.divider()

# 1. Registration Type
reg_type = st.radio("등록 유형", ["매물 내놓기 (공급)", "매물 구하기 (수요)"], horizontal=True)

# 2. Unified Form
st.markdown("### 상세 정보 입력")
st.info("정확한 매칭을 위해 아래 항목을 상세히 입력해주세요.")

form_data = render_complete_property_form()

st.divider()

# 3. Contact Info
c1, c2 = st.columns(2)
name = c1.text_input("신청자명", placeholder="이름")
phone = c2.text_input("연락처", placeholder="010-0000-0000")

# 4. Submit
if st.button("✨ AI 사전등록 완료", type="primary", use_container_width=True):
    if not name or not phone:
        st.error("이름과 연락처를 입력해주세요.")
    else:
        st.success(f"✅ {reg_type} 등록이 완료되었습니다!")
        st.markdown(f"**{name}님**, 입력하신 조건(**{form_data['complex_name']} 등**)에 맞는 매칭 상대를 찾으면 바로 연락드리겠습니다.")
        st.json(form_data)
