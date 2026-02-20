# pages/1_REGION.py
import streamlit as st

st.set_page_config(page_title="대치1동 특성·교육환경", page_icon="🏠", layout="wide")
st.title("🏠 대치1동 특성 · 교육환경(학군)")
st.caption("대치1동 학군 선호 논지를 먼저 이해 → 그 다음 AI 추천/매칭으로 이어집니다.")

# ✅ 여기부터는 새로 정리된 '심플 스토리텔링'
st.subheader("핵심 논지(한 줄)")
st.write("대치1동은 **학군(전입 시나리오)**이 주거 선택을 결정하는 교육특구입니다.")

st.subheader("학군 선호 라인(요약)")
st.markdown("- 래미안대치팰리스/대치SK뷰 → 대치초 → 대청중 → 숙명 → 단대\n- 대치아이파크 → 대도초 → 숙명(여) → 단대(부)\n- 삼환아르노보2 → 학군 세컨하우스/렌트 수요")

st.divider()

# ✅ 레거시 보존: 통합 전 화면으로 이동 버튼 2개
st.subheader("📎 기존 화면(레거시) 바로가기")
c1, c2 = st.columns(2)
with c1:
    # 예: 예전에 지도/학군을 보여주던 페이지가 있었다면 그 파일로 링크
    st.page_link("pages/legacy_map_school.py", label="📎 (레거시) 교육/학군 지도 보기", use_container_width=True)
with c2:
    st.page_link("pages/legacy_dashboard.py", label="📎 (레거시) 대시보드/요약 보기", use_container_width=True)

st.info("레거시 페이지 파일명은 실제 프로젝트에 맞게 연결만 바꾸면 됩니다. (기존 디자인/데이터 그대로 유지)")
