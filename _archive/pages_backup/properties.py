import streamlit as st
from services.excel_loader import load_properties_from_excel
from services.ga_helper import track_once, track

st.set_page_config(page_title="전체 매물", layout="wide")

track_once("view_page", {
    "page_name": "properties",
    "section": "list"
})

st.title("🟢 전체 매물 목록")

items = load_properties_from_excel()

for i, p in enumerate(items, start=1):
    name = p.get("complex_name") or p.get("name") or "매물"
    with st.container(border=True):
        st.write(name)

        if st.button("AI 매칭", key=f"match_{i}"):
            track("click_ai_matching", {
                "source": "properties",
                "property_name": name
            })
            st.session_state["matching_seed_property"] = p
            st.switch_page("pages/ai_matching_reservation.py")
