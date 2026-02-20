import streamlit as st
from services.excel_loader import load_properties_from_excel
from services.ga_helper import track_once, track

st.set_page_config(page_title="저평가 추천", layout="wide")

# GA4 페이지 진입 1회 기록
track_once("view_page", {
    "page_name": "undervalued",
    "section": "recommendation"
})

st.title("🔵 저평가 추천 매물")

items = load_properties_from_excel()

if not items:
    st.warning("매물 데이터가 없습니다.")
    st.stop()

ranked = []
for p in items:
    score = 0
    if "급매" in str(p.get("features", "")):
        score += 10
    try:
        score += float(p.get("discount_rate", 0) or 0)
    except:
        pass
    ranked.append((score, p))

ranked.sort(reverse=True, key=lambda x: x[0])

for i, (s, p) in enumerate(ranked[:20], start=1):
    name = p.get("complex_name") or p.get("name") or "매물"
    with st.expander(f"{i}. {name} | score={s}"):
        st.json(p)
        if st.button("상세 보기", key=f"detail_{i}"):
            track("click_property_detail", {
                "source": "undervalued",
                "rank": i,
                "property_name": name
            })
            st.session_state["selected_property"] = p
            st.switch_page("pages/02_properties.py")
