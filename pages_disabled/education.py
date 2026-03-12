import streamlit as st

st.set_page_config(page_title="교육환경 | 대치", page_icon="🟢", layout="wide")

def _safe_import():
    try:
        from services.local_market import local_market_svc
    except Exception:
        local_market_svc = None

    try:
        from services.ui import render_bottom_nav, scroll_to_top
    except Exception:
        render_bottom_nav, scroll_to_top = None, None

    return local_market_svc, render_bottom_nav, scroll_to_top

def main():
    local_market_svc, render_bottom_nav, scroll_to_top = _safe_import()

    st.markdown("## 🟢 01 지역정보 · 교육환경")
    st.caption("교육환경 보기 (education.py)")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("🔵 대치1동 특성 보기로 이동 (legacy_01_daechi_info.py)"):
            try:
                st.switch_page("pages/legacy_01_daechi_info.py")
            except Exception:
                st.warning("사이드바에서 legacy_01_daechi_info 페이지를 선택해주세요.")
    with col2:
        st.info("여기에 학군라인/학교/학원가/통학 동선 등 교육 콘텐츠를 구성합니다.")

    st.divider()

    if local_market_svc is None:
        st.warning("services.local_market.local_market_svc 를 찾지 못했습니다. (데모 모드)")
        st.markdown("- 예: 대치초 → 대청중 → 단대부고 라인 설명\n- 예: 학원가 밀집, 통학/학부모 수요")
    else:
        data = None
        for fn_name in ["get_education_summary", "get_school_info", "get_daechi_education"]:
            fn = getattr(local_market_svc, fn_name, None)
            if callable(fn):
                try:
                    data = fn()
                    break
                except Exception as e:
                    st.error(f"{fn_name} 호출 실패: {e}")

        if data is None:
            st.warning("교육환경 데이터 함수(get_education_summary 등)가 없습니다. (연동 대기)")
        else:
            # st.success("교육환경 로딩 성공")
            # st.json(data)
            
            st.markdown("### 🏫 대치동 명문 학군 라인업")
            
            st.info(f"💡 {data.get('description', '대치동 교육 환경 정보입니다.')}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("#### 🎒 초등학교")
                for s in data.get('elementary', []):
                    st.text(f"• {s}")
            with c2:
                st.markdown("#### 🏫 중학교")
                for s in data.get('middle', []):
                    st.text(f"• {s}")
            with c3:
                st.markdown("#### 🎓 고등학교")
                for s in data.get('high', []):
                    st.text(f"• {s}")
            
            st.divider()
            st.markdown("#### 📚 대치동 학원가 (Academy Zone)")
            st.error(data.get('academy_zone', "정보 없음"))

    st.divider()
    if render_bottom_nav:
        render_bottom_nav(current_page_label="education")
    if scroll_to_top and st.button("⬆️ 맨 위로"):
        scroll_to_top()

if __name__ == "__main__":
    main()
