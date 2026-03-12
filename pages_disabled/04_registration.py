# pages/04_registration.py
import streamlit as st
from services.ui_brand import brand_header

# ⚠️ set_page_config()는 app.py에서만 호출 (중복 제거)

brand_header(
    title="📝 매물등록 (수요자 → 공급자)",
    subtitle="수요자가 먼저 '예약/조건'을 남기고, 공급자는 그 수요에 맞춰 등록되게 설계합니다.",
    key_message="등록은 **수요자 우선**으로 받아 매칭 정확도를 올리고, 공급자는 '매칭된 수요'가 보이는 상태에서 등록되게 하여 계약 효율을 높입니다.",
    highlight_badges=["수요자 우선", "매칭 정확도", "실무 효율"],
    cta_links=[("🤖 AI 매칭", "pages/03_ai_matching.py"), ("🎬 숏츠 홍보", "pages/05_shorts.py")],
)

st.divider()

st.subheader("📎 기존 화면(레거시) 바로가기")
b1, b2 = st.columns(2)
with b1:
    st.page_link("pages/registration.py", label="📎 (레거시) 등록 폼/로직", use_container_width=True)
with b2:
    st.page_link("pages/ai_pre_register_legacy.py", label="📎 (레거시) 사전등록", use_container_width=True)

st.divider()

st.subheader("🔁 기존 시스템(레거시) 본문")
st.info("👇 위 '(레거시) 등록 폼/로직' 버튼을 클릭하면 기존 등록 화면으로 이동합니다.")

# 간단한 등록 안내
with st.container(border=True):
    st.markdown("""
**📝 매물 등록 순서**

1. **수요자 조건 먼저 입력** — 어떤 조건의 매물을 찾는지 등록
2. **AI 매칭** → 조건에 맞는 공급 매물 자동 추천  
3. **공급자 등록** → 수요가 있는 상태에서 등록하여 계약 효율 UP

> 📞 직접 등록 문의: **02-578-8285 / 010-8985-8945**
""")
