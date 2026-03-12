# pages/05_shorts.py
import streamlit as st
from services.ui_brand import brand_header

# ⚠️ set_page_config()는 app.py에서만 호출 (중복 제거)

brand_header(
    title="🎬 숏츠매물 (AI 자동홍보)",
    subtitle="매물 1개 → 숏츠/썸네일/배포문구 자동 생성 → 네이버·카카오·SNS 확산",
    key_message="좋은 매물도 노출이 없으면 계약이 느립니다. 숏츠 자동홍보는 **리드 유입을 누적**시키고, AI 매칭으로 바로 연결해 **전환율을 끌어올립니다.**",
    highlight_badges=["자동홍보", "리드 누적", "전환율 상승"],
    cta_links=[("⭐ 추천매물", "pages/02_properties.py"), ("🤖 AI 매칭", "pages/03_ai_matching.py")],
)

st.divider()

st.subheader("📎 기존 화면(레거시) 바로가기")
b1, b2 = st.columns(2)
with b1:
    st.page_link("pages/shorts.py", label="📎 (레거시) 숏츠 생성", use_container_width=True)
with b2:
    st.page_link("pages/youtuber_lab.py", label="📎 (레거시) YOU-LAB", use_container_width=True)

st.divider()

st.subheader("🔁 기존 시스템(레거시) 본문")
st.info("👇 위 버튼을 클릭하면 기존 숏츠 생성 화면으로 이동합니다.")

with st.container(border=True):
    st.markdown("""
**🎬 AI 자동홍보 프로세스**

1. **매물 선택** → AI 추천매물 탭에서 홍보 대상 선택
2. **자동 생성** → 숏츠 스크립트 + 썸네일 + 배포 문구 자동 제작
3. **멀티채널 배포** → 네이버, 카카오, 유튜브 숏츠, SNS 동시 발행
4. **리드 유입** → 클릭 → AI 매칭 챗봇으로 자동 연결

> 🚀 관리자 패널에서 숏츠 자동 생성 및 발행을 운영할 수 있습니다.
""")
