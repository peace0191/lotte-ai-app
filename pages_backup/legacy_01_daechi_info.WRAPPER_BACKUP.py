import importlib
import streamlit as st
from services.ui_brand import brand_header

st.set_page_config(page_title="대치1동 특성·교육환경", page_icon="🏠", layout="wide")

brand_header(
    title="🏠 대치1동 특성 · 교육환경(학군)",
    subtitle="‘왜 대치1동인가’를 먼저 이해 → 이후 추천/매칭 전환이 빨라집니다.",
    key_message="아래 버튼으로 ‘대치1동특성’과 ‘교육환경’을 기존 자료 그대로 복원해서 확인하세요.",
    highlight_badges=["교육특구 특화", "학군/전입 흐름", "레거시 완전 복원"],
    cta_links=[("⭐ 추천매물", "pages/02_properties.py"), ("🤖 AI 매칭", "pages/03_ai_matching.py")],
)

st.divider()

# query param
view = st.query_params.get("view", "")

# 버튼 CSS
st.markdown("""
<style>
.legacy-btn-row{display:flex; gap:14px; flex-wrap:wrap; margin: 8px 0 14px 0;}
.legacy-btn{
  display:inline-flex; align-items:center; justify-content:center;
  padding:14px 18px; border-radius:12px; font-weight:900;
  text-decoration:none !important;
  border:1px solid rgba(255,255,255,.14);
  box-shadow: 0 6px 18px rgba(0,0,0,.25);
  min-width: 240px;
}
.legacy-sky{background:#5aa9ff; color:#06121f;}
.legacy-green{background:#4fd28f; color:#04140c;}
.legacy-btn:hover{transform: translateY(-1px); filter: brightness(1.03);}
.legacy-hint{opacity:.85; font-size:.92rem; margin-top: 4px;}
@media(max-width:768px){ .legacy-btn{min-width:100%;} }
</style>
""", unsafe_allow_html=True)

# 하단 컬러 버튼 2개
st.markdown("""
<div class="legacy-btn-row">
  <a class="legacy-btn legacy-sky" href="?view=spec">🔵 대치1동특성 보기</a>
  <a class="legacy-btn legacy-green" href="?view=edu">🟢 교육환경 보기</a>
</div>
<div class="legacy-hint">※ 버튼을 누르면 아래에 ‘기존 화면’이 그대로 복원되어 출력됩니다.</div>
""", unsafe_allow_html=True)

st.divider()

def render_legacy(module_name: str):
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "main"):
            mod.main()
    except Exception as e:
        st.error("레거시 화면을 불러오지 못했습니다. (파일/모듈명 확인 필요)")
        st.code(f"{module_name}\n\n{e}")

if view == "spec":
    st.subheader("🔵 대치1동특성 (기존 자료 복원)")
    with st.expander("펼쳐보기 / 접기", expanded=True):
        render_legacy("pages.legacy_01_daechi_info")

elif view == "edu":
    st.subheader("🟢 교육환경 (기존 자료 복원)")
    with st.expander("펼쳐보기 / 접기", expanded=True):
        render_legacy("pages.education")

else:
    st.info("하단 버튼을 눌러 ‘대치1동특성’ 또는 ‘교육환경’을 기존 화면 그대로 복원하세요.")
    st.caption("원칙 유지: 메뉴는 홈+5개만 노출 / 레거시는 메뉴에 숨김 / 이 페이지 내부에서만 복원 실행")
