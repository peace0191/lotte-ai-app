from __future__ import annotations
import streamlit as st
import random
import time
from dataclasses import dataclass

@dataclass
class OTPState:
    phone: str = ""
    name: str = ""
    code: str = ""
    sent_at: float = 0.0

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"

def send_otp_demo(state: OTPState) -> OTPState:
    """데모용: 실제 SMS 대신 코드만 생성(화면에 표시)"""
    state.code = generate_otp()
    state.sent_at = time.time()
    return state

def verify_otp(state: OTPState, user_code: str, ttl_sec: int = 180) -> bool:
    if not state.code:
        return False
    if time.time() - state.sent_at > ttl_sec:
        return False
    return user_code.strip() == state.code

def login_gate():
    """
    사용자 인증(로그인) 게이트.
    로그인되지 않은 경우 이름/전화번호 입력을 요구하고 실행을 중단(st.stop)합니다.
    """
    if "is_logged_in" not in st.session_state:
        st.session_state["is_logged_in"] = False

    if not st.session_state["is_logged_in"]:
        # 로그인 화면 렌더링
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
            st.title("롯데타워 AI 부동산")
            st.markdown("##### 🔐 본인 확인 후 입장 가능합니다.")
            
            with st.form("login_form"):
                name = st.text_input("이름", placeholder="예: 홍길동")
                phone = st.text_input("휴대폰 번호", placeholder="예: 010-1234-5678")
                submitted = st.form_submit_button("인증번호 받기 및 로그인", use_container_width=True, type="primary")
                
                if submitted:
                    if name and phone:  
                        # 간단한 데모용 로직: 입력만 하면 통과
                        # 관리자 백도어: 특정 이름이나 번호 입력 시 관리자 부여 가능
                        if name == "관리자" or phone.endswith("0000"):
                            st.session_state["role"] = "admin"
                        else:
                            st.session_state["role"] = "user"
                            
                        st.session_state["user_name"] = name
                        st.session_state["user_phone"] = phone
                        st.session_state["is_logged_in"] = True
                        st.success(f"환영합니다, {name}님!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("이름과 휴대폰 번호를 올바르게 입력해주세요.")
        
        st.stop() # 로그인 전까지 앱 실행 중단

def require_admin():
    """관리자 권한 확인"""
    # sales_system 등에서 호출됨.
    # 로그인 게이트가 통과된 상태라고 가정하지만, role 확인
    if st.session_state.get("role") != "admin":
        st.error("⛔ 관리자 전용 메뉴입니다. 접근 권한이 없습니다.")
        st.stop()
