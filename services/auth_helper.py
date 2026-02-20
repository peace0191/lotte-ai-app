from __future__ import annotations

import streamlit as st
from typing import Dict, Optional

def require_role(*allowed: str) -> Dict[str, str]:
    """
    Check if user is logged in and has required role.
    If not, show error and stop execution.
    Roles: 'supplier', 'admin'
    """
    auth = st.session_state.get("auth")
    
    if not auth:
        st.error("🔒 로그인이 필요합니다. 사이드바 메뉴에서 '로그인' 페이지로 이동해주세요.")
        st.stop()
        
    user_role = auth.get("role", "supplier")
    
    if allowed and user_role not in allowed:
        st.error(f"🚫 권한이 없습니다. (필요 권한: {', '.join(allowed)})")
        st.stop()
        
    return auth

def current_user() -> Optional[Dict[str, str]]:
    """Return current user dict or None if not logged in."""
    return st.session_state.get("auth")
