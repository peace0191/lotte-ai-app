# pages/02_properties.py
import streamlit as st
from services.ui_brand import brand_header

# ⚠️ st.set_page_config()는 app.py에서만 호출 (중복 제거)

brand_header(
    title="⭐ AI 추천매물 (저평가 자동 추천)",
    subtitle="학군·렌트·투자·VIP 목적에 맞춰 '저평가 시그널' 중심으로 빠르게 선별합니다.",
    key_message="AI는 **대치1동 목적 적합도 + 저평가 시그널 + 일정/리스크**를 합쳐 '바로 예약 가능한 후보'를 먼저 제시합니다.",
    highlight_badges=["저평가 시그널", "목적별 추천", "예약 유도"],
    cta_links=[("🤖 매칭/계약", "pages/03_ai_matching.py"), ("🎬 숏츠 홍보", "pages/05_shorts.py")],
)

st.divider()

st.subheader("📎 기존 화면(레거시) 바로가기")
st.info("💡 아래 '(레거시) 매물 목록/상세'를 클릭하면 상세 매물 목록을 볼 수 있습니다.")

# ── 레거시 매물 전체 목록 직접 임베드 ───────────────────────
try:
    import json
    from pathlib import Path
    from services.meta_ops import list_all_property_ids, read_meta

    pids = list_all_property_ids()
    if not pids:
        st.warning("assets/properties/ 아래에 매물 폴더가 없습니다.")
        st.info("🧰 미디어 업로드 센터에서 신규 매물을 먼저 생성하세요.")
    else:
        st.subheader("📋 매물 목록")
        q = st.text_input("🔍 검색", placeholder="단지명, 주소, 매물ID…")

        for pid in pids[:50]:
            meta = read_meta(pid) or {}
            title = meta.get("title") or meta.get("name") or f"매물 {pid}"
            address = meta.get("address") or ""
            gap = meta.get("market_gap_percent")

            blob = f"{pid} {title} {address}".lower()
            if q and q.lower() not in blob:
                continue

            with st.container(border=True):
                st.markdown(f"**🏠 {title}**")
                if address:
                    st.caption(f"📍 {address}")
                if gap not in (None, ""):
                    st.caption(f"저평가 {gap}%")
                st.caption(f"ID: {pid}")

except Exception as e:
    st.warning(f"매물 목록을 불러오지 못했습니다: {e}")
    st.info("관리자에게 문의하거나 '미디어 업로드 센터'에서 매물을 먼저 등록해 주세요.")
