# app.py (핵심만 교체/반영)
import streamlit as st
from services.admin_gate import is_admin, admin_login_ui

st.set_page_config(page_title="대치1동 교육특구 AI 부동산", page_icon="🏠", layout="wide")

OFFICE = "롯데타워앤강남빌딩부동산중개 (주)"
CEO = "이상수"
TEL = "02-578-8285 / 010-8985-8945"

# ✅ Streamlit Navigation: 메뉴를 우리가 '직접' 구성
pages = {
    "메인": [
        st.Page("pages/01_daechi_info.py", title="🏠 대치1동 특성·교육환경", icon="🏠"),
        st.Page("pages/02_properties.py", title="⭐ AI 추천매물", icon="⭐"),
        st.Page("pages/03_ai_matching.py", title="🤖 AI 매칭(시그널+챗봇)", icon="🤖"),
        st.Page("pages/04_registration.py", title="📝 매물등록(수요자→공급자)", icon="📝"),
        st.Page("pages/05_shorts.py", title="🎬 숏츠매물(AI 자동홍보)", icon="🎬"),
    ]
}

# 🔒 관리자 메뉴는 admin일 때만 추가 → 일반 사용자는 '목록에서' 안 보임
if is_admin():
    pages["관리자"] = [
        st.Page("pages/90_admin_center.py", title="⚙️ 관리자 센터", icon="⚙️"),
    ]

nav = st.navigation(pages)
with st.sidebar:
    st.markdown(f"### {OFFICE}")
    st.caption("교육특구 특성 → AI 자동매칭 → AI 자동홍보")
    st.divider()
    admin_login_ui()
    st.caption(f"대표 {CEO} · {TEL}")

nav.run()
