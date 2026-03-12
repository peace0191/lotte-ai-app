# pages/01_daechi_info.py
import importlib
import streamlit as st
from services.ui_brand import brand_header

# ⚠️ set_page_config()는 app.py에서만 호출 (중복 제거)

brand_header(
    title="🏠 대치1동 특성 · 교육환경(학군)",
    subtitle="왜 대치1동인가 → 이해 → 추천 → 매칭 → 계약",
    key_message="대치1동은 학군 중심 시장입니다. 아래 버튼으로 기존 자료를 그대로 복원해 확인하세요.",
    highlight_badges=["교육특구 특화", "학군 흐름", "레거시 완전 복원"],
    cta_links=[("⭐ 추천매물", "pages/02_properties.py"),
               ("🤖 AI 매칭", "pages/03_ai_matching.py")]
)

st.divider()

view = st.query_params.get("view", "")

st.markdown("""
<style>
.btn-row{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0 20px 0;}
.btn{
 padding:14px 18px;border-radius:12px;font-weight:800;
 text-decoration:none !important;min-width:240px;text-align:center;
}
.sky{background:#5aa9ff;color:#001a33;}
.green{background:#4fd28f;color:#002211;}
@media(max-width:768px){
 .btn{min-width:100%;}
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="btn-row">
 <a class="btn sky" href="?view=spec">🔵 대치1동특성 보기</a>
 <a class="btn green" href="?view=edu">🟢 교육환경 보기</a>
</div>
""", unsafe_allow_html=True)

st.divider()

def render_legacy(module_name: str):
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "main"):
            mod.main()
        # Fallback if no main function
    except Exception as e:
        st.error(f"레거시 로딩 실패: {module_name}")
        st.code(str(e))

if view == "spec":
    st.markdown("### 🔵 대치1동특성 (기존 자료 복원)")
    with st.expander("📂 펼쳐보기 / 접기", expanded=True):
        render_legacy("pages.legacy_01_daechi_info")
    st.markdown("<script>window.scrollTo(0,500);</script>", unsafe_allow_html=True)

elif view == "edu":
    st.markdown("### 🟢 교육환경 (기존 자료)")
    with st.expander("📂 펼쳐보기 / 접기", expanded=True):
        render_legacy("pages.education")
    st.markdown("<script>window.scrollTo(0,500);</script>", unsafe_allow_html=True)

else:
    st.info("위 버튼을 눌러 기존 자료를 복원하세요.") 
    st.caption("기본 프레임: 메뉴는 홈+5개만 노출 / 레거시는 메뉴에 숨김 / 이 페이지 내부에서만 복원 실행")
