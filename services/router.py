from __future__ import annotations
import streamlit as st

def set_query_params(**kwargs):
    """
    Sets query parameters in a cross-version compatible way.
    If using Streamlit >= 1.29 (or newer), st.query_params is a mutable mapping.
    If using older Streamlit, st.experimental_set_query_params is used.
    """
    try:
        # Check if st.query_params is a standard dict-like object (mutable)
        # In newer Streamlit versions, st.query_params supports item assignment.
        st.query_params.clear()
        for k, v in kwargs.items():
            if v is None:
                continue
            st.query_params[k] = str(v)
    except Exception:
        # Older Streamlit versions used experimental_set_query_params
        # Or this could happen if st.query_params is not mutable (older versions of experimental_get_query_params)
        try:
            st.experimental_set_query_params(**{k: str(v) for k, v in kwargs.items() if v is not None})
        except:
             pass

def get_query_param(key: str, default: str | None = None) -> str | None:
    try:
        # Newer streamlit
        v = st.query_params.get(key)
        if v is None:
            return default
        # st.query_params in newer versions returns string directly or list depending on query
        # But typically string if singular
        if isinstance(v, list):
            return v[0] if v else default
        return str(v)
    except Exception:
        # Older streamlit
        try:
            qp = st.experimental_get_query_params()
            vv = qp.get(key, [default])
            return vv[0] if vv else default
        except:
            return default

def goto_property_detail(property_id: str, origin: str = "list", source: str = "op3"):
    """
    Navigates to the property detail view by setting query parameters.
    """
    set_query_params(pid=property_id, view="detail", origin=origin, src=source)
    
    # ⚠️ IMPORTANT: This string MUST match the actual page name/menu label for the detail view.
    # The user mentioned "🏢 매물 상세" or similar.
    # In app.py, tabs are used, not pages.
    # So we set a session state variable to switch the tab.
    # Wait, the user's snippet suggests "st.session_state['redirect_to']".
    # We should stick to what app.py expects. In app.py line 1144, it uses "manual_nav_target".
    # And line 1147: st.session_state["manual_nav_target"] = "⭐ 추천매물"
    # The user might want a NEW detail view or reuse the "⭐ 추천매물" tab but showing detail content.
    
    # I will set BOTH just in case.
    st.session_state["manual_nav_target"] = "⭐ 추천매물"
    st.session_state["redirect_to"] = "⭐ 추천매물" # Fallback if specific logci uses this
    st.rerun()
