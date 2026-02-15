# services/admin_gate.py
import streamlit as st

def is_admin() -> bool:
    # 데모용: URL에 ?admin=1
    q = st.query_params.get("admin")
    if q == "1":
        return True

    # 운영용: 세션 관리자 토큰
    return st.session_state.get("is_admin", False)

def require_admin():
    if not is_admin():
        st.error("🔒 관리자 전용 메뉴입니다.")
        st.stop()

def admin_login_ui():
    """secrets.toml에 ADMIN_KEY 넣으면 사용"""
    with st.expander("🔒 관리자 로그인", expanded=False):
        key = st.text_input("ADMIN KEY", type="password")
        real = st.secrets.get("ADMIN_KEY", "")
        if st.button("로그인"):
            if real and key == real:
                st.session_state["is_admin"] = True
                st.success("관리자 모드 활성화")
            elif not real:
                st.warning("secrets.toml에 ADMIN_KEY가 설정되지 않았습니다.")
            else:
                st.error("키가 올바르지 않습니다.")
