# pages/00_HOME.py (IR 톤 압축 버전 핵심 블록)
import streamlit as st
from services.admin_gate import is_admin, admin_login_ui

# ⚠️ st.set_page_config()는 app.py에서만 호출 (중복 제거)

OFFICE = "롯데타워앤강남빌딩부동산중개 (주)"
CEO = "이상수"
TEL_MAIN = "02-578-8285"
TEL_MOBILE = "010-8985-8945"

st.title("🏠 대치1동 교육특구 AI 부동산")
st.caption("교육특구 특성 → AI 자동매칭 → AI 자동홍보 | ‘3마리 토끼’를 한 앱에 담은 전환형 부동산 시스템")

left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader("IR 한 줄 요약")
    st.write("**대치1동 교육특구 ‘국지 특성’에 최적화된 AI가 저평가 매물을 추천·예약·계약 매칭하고, 숏츠 자동홍보로 리드를 확산해 전환율/수익을 극대화합니다.**")

    st.divider()
    st.subheader("💎 3마리 토끼(핵심 가치)")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### ① 교육특구 이해\n- 학군/전입 시나리오\n- 단지별 선호 맵\n- 고객의 ‘왜’ 확정")
    with c2:
        st.markdown("### ② 자동매칭\n- 저평가 선별\n- 예약→상담→계약\n- 체크리스트 표준화")
    with c3:
        st.markdown("### ③ 자동홍보\n- 숏츠/3D투어\n- 네이버/카카오/SNS\n- 리드 유입 누적")

    st.divider()
    st.subheader("📈 전환 퍼널(수익극대화 구조)")
    st.markdown(
        """
1) **탐색**: 대치1동 교육특구 특성(학군/전입 흐름)로 고객 목적을 분류  
2) **추천**: 목적(학군·렌트·투자·VIP)에 맞는 **저평가 매물** 우선 추천  
3) **예약**: 수요자 등록/예약 → 담당자 우선 라우팅  
4) **매칭**: AI 시그널+챗봇으로 상담 효율↑, 계약 속도↑  
5) **홍보**: 숏츠 자동 생성/배포 → 리드 유입 확대 → 반복 전환
"""
    )

    st.divider()
    st.subheader("🚀 핵심 메뉴(홈+5개)")
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1: st.page_link("pages/01_daechi_info.py", label="🏠 지역정보", use_container_width=True)
    with b2: st.page_link("pages/02_properties.py", label="⭐ 추천매물", use_container_width=True)
    with b3: st.page_link("pages/03_ai_matching.py", label="🤖 AI 매칭", use_container_width=True)
    with b4: st.page_link("pages/04_registration.py", label="📝 매물등록", use_container_width=True)
    with b5: st.page_link("pages/05_shorts.py", label="🎬 숏츠매물", use_container_width=True)

with right:
    st.subheader("📞 상담/문의")
    st.info(
        f"""**{OFFICE}**
대표: **{CEO}**
전화: **{TEL_MAIN}**
모바일: **{TEL_MOBILE}**"""
    )
    admin_login_ui()
    if is_admin():
        st.success("관리자 모드 ON")
        st.page_link("pages/90_admin_center.py", label="⚙️ 관리자 센터", use_container_width=True)

st.caption("※ 레거시 페이지는 메뉴에 노출하지 않고, 각 메뉴 내부의 ‘레거시 버튼 2개 + 레거시 본문’으로만 복원 실행합니다.")
