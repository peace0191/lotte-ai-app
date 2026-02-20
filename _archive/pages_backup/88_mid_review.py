import streamlit as st

st.set_page_config(page_title="중간평가", page_icon="🧪", layout="wide")

st.title("🧪 중간평가: 지금까지 연결 상태 점검")

st.caption("이 페이지는 현재 프로젝트의 연결 상태(GA4/AB/매물/매칭/리드/VIP)를 한 번에 점검합니다.")

# ----------------------------
# Safe imports
# ----------------------------
def safe_imports():
    out = {}

    # GA helper
    try:
        from services.ga_helper import track_once, track
        out["ga_helper"] = (True, track_once, track, None)
    except Exception as e:
        out["ga_helper"] = (False, None, None, str(e))

    # GA4 tracking
    try:
        from services.ga4_tracking import ga_event
        out["ga4"] = (True, ga_event, None)
    except Exception as e:
        out["ga4"] = (False, None, str(e))

    # AB helper
    try:
        from services.ab_helper import get_variant
        out["ab"] = (True, get_variant, None)
    except Exception as e:
        out["ab"] = (False, None, str(e))

    # Properties loader
    try:
        from services.excel_loader import load_properties_from_excel
        out["excel_loader"] = (True, load_properties_from_excel, None)
    except Exception as e:
        out["excel_loader"] = (False, None, str(e))

    # Matching service
    try:
        from services.matching_svc import matching_svc
        out["matching"] = (True, matching_svc, None)
    except Exception as e:
        out["matching"] = (False, None, str(e))

    return out

imp = safe_imports()

# ----------------------------
# Section: Health check cards
# ----------------------------
st.markdown("## ✅ 연결 상태")

cols = st.columns(5)

# GA helper
ok, _, _, err = imp["ga_helper"]
cols[0].metric("GA Helper", "OK" if ok else "FAIL")
if not ok:
    cols[0].caption(err)

# GA4
ok, _, err = imp["ga4"]
cols[1].metric("GA4", "OK" if ok else "FAIL")
if not ok:
    cols[1].caption(err)

# AB
ok, _, err = imp["ab"]
cols[2].metric("A/B", "OK" if ok else "FAIL")
if not ok:
    cols[2].caption(err)

# Loader
ok, _, err = imp["excel_loader"]
cols[3].metric("매물 로더", "OK" if ok else "FAIL")
if not ok:
    cols[3].caption(err)

# Matching
ok, _, err = imp["matching"]
cols[4].metric("매칭 엔진", "OK" if ok else "FAIL")
if not ok:
    cols[4].caption(err)

st.divider()

# ----------------------------
# Section: GA test button
# ----------------------------
st.markdown("## 📡 GA4 이벤트 테스트")
if imp["ga_helper"][0]:
    track_once, track = imp["ga_helper"][1], imp["ga_helper"][2]
    # page view once
    track_once("view_page", {"page_name": "mid_review", "section": "qa"})

    if st.button("GA4 테스트 이벤트 보내기"):
        track("qa_test_event", {"where": "mid_review"})
        st.success("✅ qa_test_event 전송 시도 완료 (GA4 DebugView에서 확인 가능)")
else:
    st.warning("services/ga_helper.py가 없어 GA 테스트를 수행할 수 없습니다.")

st.divider()

# ----------------------------
# Section: A/B test demo
# ----------------------------
st.markdown("## 🧪 A/B 테스트 현재 배정 확인")
if imp["ab"][0]:
    get_variant = imp["ab"][1]
    v = get_variant("cta_button_test")
    st.info(f"현재 세션의 cta_button_test 배정: **{v}**")
else:
    st.warning("services/ab_helper.py가 없어 A/B 배정을 확인할 수 없습니다.")

st.divider()

# ----------------------------
# Section: Properties preview
# ----------------------------
st.markdown("## 🏠 매물 로딩 미리보기")
if imp["excel_loader"][0]:
    load_properties_from_excel = imp["excel_loader"][1]
    try:
        items = load_properties_from_excel()
    except Exception as e:
        st.error(f"매물 로딩 실패: {e}")
        items = []

    st.write(f"불러온 매물 수: **{len(items)}**")
    if items:
        st.json(items[0])
        st.caption("첫 번째 매물 1건을 표시했습니다.")
else:
    st.warning("excel_loader 연결 실패로 매물 미리보기를 할 수 없습니다.")

st.divider()

# ----------------------------
# Section: Matching status / VIP
# ----------------------------
st.markdown("## 🔥 매칭 / VIP 상태")
if imp["matching"][0]:
    matching_svc = imp["matching"][1]

    st.write(f"대기 리드 수(match_reservations): **{len(matching_svc.match_reservations)}**")

    if matching_svc.match_reservations:
        latest = matching_svc.match_reservations[-1]
        st.subheader("최근 리드(마스킹 전 원본)")
        st.json(latest)

        if latest.get("status") == "VIP_HOT":
            st.warning(f"🔥 VIP_HOT 감지: {latest['conditions'].get('user_name')}")
            st.toast("🔥 VIP_HOT 리드 발생!", icon="🔥")
        else:
            st.info("최근 리드는 VIP_HOT가 아닙니다.")

    st.divider()
    st.markdown("### 🔐 마스킹된 리드 보기")
    if st.button("마스킹 리스트 출력"):
        try:
            masked = matching_svc.get_masked_reservations()
            st.json(masked)
        except Exception as e:
            st.error(f"마스킹 리스트 실패: {e}")

else:
    st.warning("matching_svc 연결 실패로 매칭/VIP 상태를 확인할 수 없습니다.")

st.divider()
st.markdown("## ✅ 다음 체크")
st.markdown(
"""
- **GA4 DebugView**에서 `view_page(mid_review)` / `qa_test_event
