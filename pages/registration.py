import streamlit as st
from services.matching_svc import matching_svc
from services.ui import render_bottom_nav

st.set_page_config(page_title="신규 등록", page_icon="🔵", layout="wide")
st.title("🔵 신규 등록(권장) + 즉시 매칭 알림")

with st.form("reg_form"):
    property_id = st.text_input("매물 ID (예: DAechi-xxx / 단지명 포함 가능)", "")
    agent_id = st.text_input("담당자(중개사) ID", "admin")
    status = st.selectbox("상태", ["active", "IMMEDIATE", "hold"], index=0)

    # 추가 정보(선택) - 저장만 해둠
    complex_name = st.text_input("단지/매물명", "")
    address = st.text_input("주소", "")
    memo = st.text_area("메모/특이사항", "")

    ok = st.form_submit_button("등록 + 즉시 매칭 체크")

if ok:
    if not property_id:
        st.error("매물 ID는 필수입니다.")
        st.stop()

    # (선택) 등록 정보 세션 저장
    st.session_state["last_registered_listing"] = {
        "property_id": property_id,
        "agent_id": agent_id,
        "status": status,
        "complex_name": complex_name,
        "address": address,
        "memo": memo,
    }

    st.success("매물 등록 저장 완료(세션). 이제 즉시 매칭 체크합니다.")

    try:
        alerts = matching_svc.register_new_listing(property_id=property_id, agent_id=agent_id, status=status)
        if alerts:
            st.warning("📣 즉시 매칭 알림 발생")
            for a in alerts:
                st.write(a)
        else:
            st.info("즉시 매칭 알림 없음(대기 리드와 조건 불일치).")
    except Exception as e:
        st.error(f"즉시 매칭 체크 실패: {e}")

render_bottom_nav(active="registration")
