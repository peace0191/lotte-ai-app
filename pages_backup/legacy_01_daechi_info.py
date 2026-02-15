import streamlit as st

st.set_page_config(page_title="레거시 | 대치1동 특성", page_icon="🔵", layout="wide")

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

    st.markdown("## 🔵 레거시 연결 · 01 지역정보")
    st.caption("대치1동 특성 보기 (legacy_01_daechi_info.py)")

    col1, col2 = st.columns([1,1])
    with col1:
        st.info("이 페이지는 ‘하늘(🔵)’ 레거시 버튼에 연결되는 고정 페이지입니다.")
    with col2:
        if st.button("🟢 교육환경 보기로 이동 (education.py)"):
            try:
                st.switch_page("pages/education.py")
            except Exception:
                st.warning("이 환경에서는 st.switch_page를 사용할 수 없습니다. 사이드바에서 education 페이지를 선택해주세요.")

    st.divider()

    if local_market_svc is None:
        st.warning("services.local_market.local_market_svc 를 찾지 못했습니다. (데모 모드)")
        st.markdown("- 여기에는 ‘대치1동 핵심 요약(학군/교통/수요/가격대)’ 같은 콘텐츠를 넣으면 됩니다.")
    else:
        # 서비스에 함수명이 무엇인지 프로젝트마다 달라서, 안전하게 탐색 호출
        data = None
        for fn_name in ["get_daechi_summary", "get_region_summary", "get_daechi_info"]:
            fn = getattr(local_market_svc, fn_name, None)
            if callable(fn):
                try:
                    data = fn()
                    break
                except Exception as e:
                    st.error(f"{fn_name} 호출 실패: {e}")

        if data is None:
            st.warning("local_market_svc에 사용할 요약 함수(get_daechi_summary 등)가 없습니다. (연동 대기)")
        else:
            # st.success("지역 정보 로딩 성공")
            # st.json(data)
            
            # Formatted UI
            st.markdown(f"### 📍 {data.get('region_name', '지역 정보')}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**🏫 학군 (School District)**")
                st.info(data.get("school_district", "-"))
                
                st.markdown("**🚇 교통 (Transport)**")
                st.text(data.get("transport", "-"))

            with c2:
                st.markdown("**📚 학원가 (Academy)**")
                st.success(data.get("academy_street", "-"))
                
                st.markdown("**📈 수요 동향 (Trend)**")
                st.warning(data.get("demand_trend", "-"))
            
            st.divider()
            
            # Price Range
            pr = data.get("price_range", {})
            st.markdown("#### 💰 시세 가이드 (Price Range)")
            m1, m2 = st.columns(2)
            m1.metric("30평형대 매매", pr.get("30py_apt", "-"))
            m2.metric("30평형대 전세", pr.get("jeonse", "-"))
            
            # Complexes
            st.markdown("#### 🏢 주요 랜드마크")
            complexes = data.get("major_complexes", [])
            st.write(", ".join(complexes))

    st.divider()
    if render_bottom_nav:
        render_bottom_nav(current_page_label="daechi")
    if scroll_to_top and st.button("⬆️ 맨 위로"):
        scroll_to_top()

if __name__ == "__main__":
    main()
