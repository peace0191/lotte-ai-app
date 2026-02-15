# pages/0_HOME.py
import streamlit as st
from services.admin_gate import is_admin, admin_login_ui

st.set_page_config(page_title="대치1동 교육특구 AI 부동산", page_icon="🏠", layout="wide")

OFFICE = "롯데타워앤강남빌딩부동산중개 (주)"
CEO = "이상수"
TEL = "02-578-8285 / 010-8985-8945"

st.title("🏠 대치1동 교육특구 AI 부동산")
st.caption("교육특구 특성 → AI 자동매칭 → AI 자동홍보 : 3가지가 한눈에 보이는 실무형 앱")

col1, col2 = st.columns([2,1], gap="large")

with col1:
    st.subheader("대표 인사말")
    st.write(
        f"""
안녕하세요. **{OFFICE}** 대표 **{CEO}**입니다.

대치1동은 **‘학군’이 곧 ‘주거 선택’이 되는 교육특구**입니다.  
저희 앱은 이 국지적 특성을 **명확히 설명(1)**하고,  
AI가 **저평가 매물을 추천·예약·계약 매칭(2)**하며,  
숏츠 기반 **자동홍보로 수요/공급을 연결(3)**해 **계약 전환을 극대화**합니다.
"""
    )

    st.divider()
    st.subheader("💎 3대 핵심 전략")
    cA, cB, cC = st.columns(3)
    with cA:
        st.markdown("### ① 교육특구 특성\n- 학군 라인/단지별 전입 흐름\n- 대치1동 ‘왜’ 이사하는가를 한 화면에")
    with cB:
        st.markdown("### ② AI 자동매칭\n- 수요자(예약) → AI 저평가 추천\n- 상담/방문/계약 체크리스트 표준화")
    with cC:
        st.markdown("### ③ AI 자동홍보\n- 숏츠/3D투어 자동 생성\n- 네이버/카카오/SNS 링크 확산")

    st.divider()
    st.subheader("📱 메뉴 바로가기(5개)")
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1: st.page_link("pages/1_REGION.py", label="🏠 지역정보", use_container_width=True)
    with b2: st.page_link("pages/2_RECOMMEND.py", label="⭐ 추천매물", use_container_width=True)
    with b3: st.page_link("pages/3_AI_MATCHING.py", label="🤖 AI 매칭", use_container_width=True)
    with b4: st.page_link("pages/4_REGISTER.py", label="📝 매물등록", use_container_width=True)
    with b5: st.page_link("pages/5_SHORTS.py", label="🎬 숏츠매물", use_container_width=True)

with col2:
    st.subheader("📞 상담/문의")
    st.info(f"{OFFICE}\n\n대표: {CEO}\n\n전화: {TEL}")

    admin_login_ui()

    if is_admin():
        st.success("관리자 모드 ON")
        st.page_link("pages/90_ADMIN.py", label="⚙️ 관리자 메뉴", use_container_width=True)

st.caption("※ 기존(레거시) 기능/데이터는 통합 메뉴 안에서 ‘레거시 버튼’으로 그대로 복원 접근 가능합니다.")
