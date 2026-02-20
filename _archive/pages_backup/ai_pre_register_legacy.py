import streamlit as st

st.set_page_config(page_title="레거시 등록(복원)", page_icon="🟢", layout="wide")

def _safe_import():
    try:
        from services.ui import render_bottom_nav, scroll_to_top
    except Exception:
        render_bottom_nav, scroll_to_top = None, None

    return render_bottom_nav, scroll_to_top

def main():
    render_bottom_nav, scroll_to_top = _safe_import()

    st.markdown("## 🟢 04 등록 · 레거시 등록(복원)")
    st.caption("ai_pre_register_legacy.py (연두 버튼 연결)")

    if st.button("🔵 신규 등록(권장)으로 이동 (registration.py)"):
        try:
            st.switch_page("pages/registration.py")
        except Exception:
            st.warning("사이드바에서 registration 페이지를 선택해주세요.")

    st.divider()
    st.warning("이 페이지는 ‘레거시 등록 복원’용 고정 엔트리입니다.")
    st.markdown(
        "- 기존에 사용하던 레거시 등록 UI/로직이 따로 있으면 이 파일에 붙이면 됩니다.\n"
        "- 아직 레거시 코드가 없으면, 현재는 ‘복원 슬롯’만 확보해 둔 상태입니다."
    )

    # 레거시 입력폼(간단)
    with st.form("legacy_reg_form"):
        raw = st.text_area("레거시 원문/메모/간단 텍스트 붙여넣기", height=180)
        ok = st.form_submit_button("임시 저장(데모)")
    if ok:
        st.session_state["legacy_registration_raw"] = raw
        st.success("임시 저장 완료(데모)")
        st.code(raw)

    st.divider()
    if render_bottom_nav:
        render_bottom_nav(active="legacy_registration")
    if scroll_to_top and st.button("⬆️ 맨 위로"):
        scroll_to_top()

if __name__ == "__main__":
    main()
