from __future__ import annotations
import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu

from services.ui import header, COMPANY
from services.auth import OTPState, send_otp_demo, verify_otp
from services.data import load_properties, load_faq_common

st.set_page_config(page_title="롯데타워 AI 영업 시스템", page_icon="🏢", layout="wide")

# --- Centralized Session State Initialization (v4.30) ---
def init_session_state():
    defaults = {
        "authed": False,
        "selected": None,
        "redirect_to": None,
        "latest_star": None,
        "star_dict": {},
        "shorts_idx": 0,
        "menu_index": 0,
        "main_menu_widget": "🎓 대치1동 특성",
        "chat": [{"role": "assistant", "content": "안녕하세요! 대치1동 명품 매물에 대해 무엇을 도와드릴까요?"}],
        "selected_property": {},
        "decision": {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_resource
def startup_sync():
    try:
        from services.csv_processor import process_csv_files
        process_csv_files()
    except Exception as e:
        print(f"Startup Sync Error: {e}")

init_session_state()
startup_sync()

if "otp" not in st.session_state:
    st.session_state.otp = OTPState()

properties = load_properties()
faq_common = load_faq_common()

def login_view():
    header()
    
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; min-height: 50vh;">
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(212, 175, 55, 0.2); padding: 40px; border-radius: 30px; width: 100%; max-width: 450px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); text-align: center;">
                <h2 style="color: #d4af37; margin-bottom: 10px; font-weight: 900;">🔐 AI 인증 로그인</h2>
                <div style="margin-bottom: 30px;">
                    <p style="color: #d4af37; font-size: 16px; font-weight: 700; margin-bottom: 5px;">롯데타워앤강남빌딩부동산중개(주)</p>
                    <p style="color: #6c757d; font-size: 13px; margin: 2px 0;">중개업등록: 11680-2023-00078</p>
                    <p style="color: #6c757d; font-size: 13px; margin: 2px 0;">사업자등록: 461-86-02740</p>
                </div>
    """, unsafe_allow_html=True)

    tab_cols = st.columns(2)
    with tab_cols[0]:
        st.markdown("""<div style="background:linear-gradient(135deg, #d4af37, #b8860b); color:#000; padding:10px; border-radius:8px; text-align:center; font-weight:700; font-size:14px; cursor:pointer;">📱 휴대폰 인증</div>""", unsafe_allow_html=True)
    with tab_cols[1]:
        st.markdown("""<div style="background:rgba(0,0,0,0.3); color:#999; padding:10px; border-radius:8px; text-align:center; font-weight:700; font-size:14px; cursor:pointer;">✉️ 이메일 로그인</div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        phone_input = st.text_input("휴대폰 번호", placeholder="010-1234-5678", key="phone_input_val")
        user_name = st.text_input("이름", placeholder="홍길동", key="name_input_val")
        send_btn = st.form_submit_button("인증번호 받기", use_container_width=True)
        
        if send_btn:
            if phone_input and user_name:
                st.session_state.otp_sent = True
                st.toast("✅ 인증번호가 발송되었습니다!", icon="📲")
            else:
                st.error("이름과 휴대폰 번호를 입력해주세요.")

    if st.session_state.get("otp_sent"):
        st.markdown("""
            <div style="background:rgba(212,175,55,0.1); border:2px dashed #d4af37; border-radius:12px; padding:20px; text-align:center; margin-bottom:20px; margin-top:20px;">
                <div style="font-size:12px; color:#d4af37; margin-bottom:8px; font-weight:700;">📲 실시간 전송된 인증번호 (데모)</div>
                <div style="font-size:32px; font-weight:900; color:#d4af37; letter-spacing:8px; font-family:'Courier New', monospace;">123456</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("otp_form"):
            otp = st.text_input("인증번호 입력", placeholder="6자리 숫자", key="otp_input_val")
            login_btn = st.form_submit_button("로그인", use_container_width=True)
            if login_btn:
                if otp == "123456":
                    st.session_state.authed = True
                    st.rerun()
                else:
                    st.error("인증번호가 일치하지 않습니다.")
            
    st.markdown("""
            </div>
        </div>
        <p style="text-align: center; color: #555; margin-top: 20px; font-size: 12px;">📧 이메일 로그인 (추후예정)</p>
    """, unsafe_allow_html=True)

def app_view():
    st.caption("🚀 BUILD: v17.00 | 2026-02-04 21:05 KST | Matching Signal Revolution")
    header()
    st.markdown("")

    if "menu_index" not in st.session_state:
        st.session_state.menu_index = 0

    menu_labels = ["🎓 대치1동 특성", "🏠 추천매물", "🎯 AI 매칭 시그널", "🚀 사전등록 매칭", "🎬 AI 숏츠", "🔴 YOU-LAB", "💬 AI 챗봇", "📚 교육환경", "🏢 영업팩 생성", "⚙️ 시스템"]
    
    # --- Redirect Manager (v4.26) ---
    if "redirect_to" in st.session_state and st.session_state["redirect_to"]:
        st.session_state["main_menu_widget"] = st.session_state["redirect_to"]
        try:
            st.session_state.menu_index = menu_labels.index(st.session_state["redirect_to"])
        except ValueError:
            pass
    st.session_state["redirect_to"] = None # Reset
    
    # --- Navigation Logic Fix (v4.31) ---
    # Handle manual navigation (from bottom nav or redirect)
    if st.session_state.get("manual_nav_target"):
        try:
            target = st.session_state["manual_nav_target"]
            st.session_state.menu_index = menu_labels.index(target)
        except ValueError:
            pass
        st.session_state["manual_nav_target"] = None

    # Ensure menu_index is valid
    if "menu_index" not in st.session_state:
        st.session_state.menu_index = 0
        
    selected = option_menu(
        None,
        menu_labels,
        icons=["mortarboard", "house", "bullseye", "rocket", "play-btn", "youtube", "chat-dots", "book", "briefcase", "gear"],
        menu_icon="cast",
        orientation="horizontal",
        default_index=st.session_state.menu_index,
        # key="main_menu_widget", # Removed to prevent state conflict
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#6c757d", "font-size": "14px"}, 
            "nav-link": {"font-size": "13px", "text-align": "center", "margin":"0px", "--hover-color": "rgba(212,175,55,0.1)", "color": "#adb5bd"},
            "nav-link-selected": {"background-color": "#ff4b4b", "color": "white", "font-weight": "bold"}, 
        }
    )

    # Sync state with selection (if user clicked menu)
    if selected in menu_labels:
        st.session_state.menu_index = menu_labels.index(selected)

    if selected == "🎓 대치1동 특성":
        import pages.dashboard as pg_dash
        pg_dash.render(properties)
    elif selected == "🏠 추천매물":
        import pages.properties as pg_props
        pg_props.render(properties)
    elif selected == "🎯 AI 매칭 시그널":
        import pages.undervalued as pg_under
        pg_under.render(properties)
    elif selected == "🚀 사전등록 매칭":
        import pages.registration as pg_reg
        pg_reg.render()
    elif selected == "🎬 AI 숏츠":
        import pages.shorts as pg_shorts
        pg_shorts.render(properties)
    elif selected == "🔴 YOU-LAB":
        import pages.youtuber_lab as pg_you
        pg_you.render(properties)
    elif selected == "💬 AI 챗봇":
        import pages.chatbot as pg_chat
        pg_chat.render(faq_common)
    elif selected == "📚 교육환경":
        import pages.education as pg_edu
        pg_edu.render()
    elif selected == "🏢 영업팩 생성":
        import pages.sales_system as pg_sales
        pg_sales.render()
    elif selected == "⚙️ 시스템":
        import pages.admin as pg_admin
        pg_admin.render(properties)
    


if not st.session_state.authed:
    login_view()
else:
    app_view()
