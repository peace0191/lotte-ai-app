import streamlit as st
from services.admin_gate import is_admin, admin_login_ui

st.set_page_config(page_title="?移???援먯쑁?밴뎄 AI 遺?숈궛", page_icon="?룧", layout="wide")

OFFICE = "濡?뜲??뚯븻媛뺣궓鍮뚮뵫遺?숈궛以묎컻 (二?"
CEO = "?댁긽??
TEL = "02-578-8285 / 010-8985-8945"

# ??Streamlit Navigation: 硫붾돱瑜??곕━媛 '吏곸젒' 援ъ꽦
pages = {
    "硫붿씤": [
        st.Page("pages/00_HOME.py", title="?룧 ???붿빟)", icon="?룧"),
        st.Page("pages/01_daechi_info.py", title="?룧 ?移????뱀꽦쨌援먯쑁?섍꼍", icon="?룧"),
        st.Page("pages/02_properties.py", title="狩?AI 異붿쿇留ㅻЪ", icon="狩?),
        st.Page("pages/03_ai_matching.py", title="?쨼 AI 留ㅼ묶(?쒓렇??梨쀫큸)", icon="?쨼"),
        st.Page("pages/04_registration.py", title="?뱷 留ㅻЪ?깅줉(?섏슂?먥넂怨듦툒??", icon="?뱷"),
        st.Page("pages/05_shorts.py", title="?렗 ?륁툩留ㅻЪ(AI ?먮룞?띾낫)", icon="?렗"),
    ]
}

# ?뵏 愿由ъ옄 硫붾돱??admin???뚮쭔 異붽? ???쇰컲 ?ъ슜?먮뒗 '紐⑸줉?먯꽌' ??蹂댁엫
if is_admin():
    pages["愿由ъ옄"] = [
        st.Page("pages/90_admin_center.py", title="?숋툘 愿由ъ옄 ?쇳꽣", icon="?숋툘"),
    ]

nav = st.navigation(pages)
with st.sidebar:
    st.markdown(f"### {OFFICE}")
    st.caption("援먯쑁?밴뎄 ?뱀꽦 ??AI ?먮룞留ㅼ묶 ??AI ?먮룞?띾낫")
    st.divider()
    admin_login_ui()
    st.caption(f"???{CEO} 쨌 {TEL}")

nav.run()
