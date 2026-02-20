# pages/03_ai_matching.py
import importlib
import streamlit as st
from services.ui_brand import brand_header

# ⚠️ set_page_config()는 app.py에서만 호출 (중복 제거)

brand_header(
    title="🤖 AI 매칭 (시그널 + 챗봇 통합)",
    subtitle="예약 리드 → 추천 → 상담 표준화 → 계약 매칭 끊김 없는 흐름",
    key_message="수요자 조건을 입력하면 AI가 저평가 후보를 제시하고, 챗봇이 질문을 해결해 계약 속도를 올립니다.",
    highlight_badges=["전환 퍼널", "수요 예측", "챗봇 이탈 방지"],
    cta_links=[("📝 등록", "pages/04_registration.py"), ("⭐ 추천매물", "pages/02_properties.py")],
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
 <a class="btn sky" href="?view=match">🔵 AI 매칭/예약 화면</a>
 <a class="btn green" href="?view=chat">🟢 AI 챗봇 실행</a>
</div>
""", unsafe_allow_html=True)

st.divider()

def render_legacy(module_name: str):
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "main"):
            mod.main()
    except Exception as e:
        st.error(f"레거시 로딩 실패: {module_name}")
        st.code(str(e))

if view == "match":
    st.markdown("### 🔵 AI 매칭/예약 (기존 화면 복원)")
    with st.expander("📂 펼쳐보기 / 접기", expanded=True):
        render_legacy("pages.ai_matching_reservation")
    st.markdown("<script>window.scrollTo(0,500);</script>", unsafe_allow_html=True)

elif view == "chat":
    st.markdown("### 🟢 AI 챗봇 (기존 화면 복원)")
    with st.expander("📂 펼쳐보기 / 접기", expanded=True):
        render_legacy("pages.chatbot")
    st.markdown("<script>window.scrollTo(0,500);</script>", unsafe_allow_html=True)

else:
    st.info("위 버튼을 눌러 AI 매칭 또는 챗봇 화면을 실행하세요.")
    st.caption("기본 프레임 유지: 메뉴 통합 & 레거시 복원")
