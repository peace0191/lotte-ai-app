from __future__ import annotations
import streamlit as st

import streamlit.components.v1 as components

def scroll_to_top():
    js = """
    <script>
        var body = window.parent.document.querySelector(".main");
        var html = window.parent.document.documentElement;
        if (body) body.scrollTop = 0;
        if (html) html.scrollTop = 0;
    </script>
    """
    components.html(js, height=0)

COMPANY = {
  "name": "롯데타워앤강남빌딩부동산중개(주)",
  "agent": "공인중개사 이상수",
  "reg": "11680-2023-00078",
  "tel": "02-578-8285",
  "mobile": "010-8985-8945",
  "addr": "서울 강남구 대치동 938 삼환아르누보 507호"
}

MENU_ORDER = ["🎓 대치1동 특성", "🏠 추천매물", "🎯 AI 매칭 시그널", "🚀 사전등록 매칭", "🎬 AI 숏츠", "🔴 YOU-LAB", "💬 AI 챗봇", "📚 교육환경", "🏢 영업팩 생성", "⚙️ 시스템"]

def render_bottom_nav(current_menu_name: str):
    try:
        idx = MENU_ORDER.index(current_menu_name)
    except ValueError:
        return
    
    st.markdown("---")
    
    # Custom Navigation Shortcuts
    c_qk1, c_qk2, c_qk3 = st.columns(3)
    c_qk1.button("📉 저평가 매물 보기", key=f"qk_underval_{idx}", use_container_width=True, on_click=lambda: st.session_state.update({"manual_nav_target": "🎯 AI 매칭 시그널"}))
    c_qk2.button("🏠 추천 매물 보기", key=f"qk_props_{idx}", use_container_width=True, on_click=lambda: st.session_state.update({"manual_nav_target": "🏠 추천매물"}))
    c_qk3.button("🚀 사전등록 매칭", key=f"qk_reg_{idx}", use_container_width=True, on_click=lambda: st.session_state.update({"manual_nav_target": "🚀 사전등록 매칭"}))
    
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    if idx > 0:
        prev_name = MENU_ORDER[idx - 1]
        with col1:
            if st.button(f"⬅️ {prev_name}", key=f"nav_prev_{idx}", use_container_width=True):
                 st.session_state["manual_nav_target"] = prev_name
                 st.rerun()
    
    with col2:
        if st.button("💬 AI 챗봇 가기", key=f"nav_chat_{idx}", use_container_width=True):
            st.session_state.menu_index = 6
            st.rerun()
             
    if idx < len(MENU_ORDER) - 1:
        next_name = MENU_ORDER[idx + 1]
        with col3:
             if st.button(f"{next_name} ➡️", key=f"nav_next_{idx}", use_container_width=True):
                 st.session_state["manual_nav_target"] = next_name
                 st.rerun()

    st.markdown(
        "<div style='margin-top:14px; opacity:0.75; font-size:12px; text-align:right;'>"
        "롯데타워앤강남빌딩부동산중개 (주) 02-578-8285"
        "</div>",
        unsafe_allow_html=True
    )

def header():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');
        
        * {
            font-family: 'Pretendard', sans-serif;
        }

        .stApp {
            background-color: #0d1117;
            background-image: radial-gradient(circle at 50% 50%, #161b22 0%, #0d1117 100%);
        }
        
        [data-testid="stHeader"] {
            background-color: rgba(13, 17, 23, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
        }

        [data-testid="stSidebarNav"] {
            display: none;
        }

        .premium-header {
            padding: 25px;
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(212, 175, 55, 0.15);
            display: flex;
            align-items: center;
            gap: 25px;
            margin-bottom: 30px;
            animation: fadeIn 0.8s ease-out;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .ceo-avatar {
            width: 90px;
            height: 90px;
            border-radius: 50%;
            border: 2px solid #d4af37;
            object-fit: cover;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
            transition: transform 0.3s ease;
        }

        .ceo-avatar:hover {
            transform: scale(1.05);
        }

        .header-content h1 {
            color: #d4af37;
            font-size: 26px;
            margin: 0;
            font-weight: 900;
            letter-spacing: -0.5px;
        }

        .header-content p {
            color: #ced4da;
            font-size: 15px;
            margin: 6px 0 0 0;
            font-weight: 500;
        }

        .header-info {
            display: flex;
            gap: 15px;
            font-size: 13px;
            color: #8b949e;
            margin-top: 12px;
        }

        /* Dashboard Styling */
        .dash-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 20px;
            text-align: center;
            transition: all 0.3s ease;
            height: 100%;
        }

        .dash-card:hover {
            border-color: #d4af37;
            transform: translateY(-5px);
            background: rgba(212, 175, 55, 0.05);
        }

        .dash-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }

        .dash-title {
            font-weight: 800;
            color: #d4af37;
            font-size: 16px;
            margin-bottom: 8px;
        }

        .dash-desc {
            font-size: 13px;
            color: #a0a0a0;
            line-height: 1.4;
        }

        /* 챗봇 하단 입력창 시인성 개선 (v4.18) */
        div[data-testid="stChatInput"] {
            background-color: #FFD700 !important; /* 황금빛 노란색 */
            border: 2px solid #d4af37 !important;
            border-radius: 15px !important;
            padding: 4px !important;
        }
        div[data-testid="stChatInput"] textarea {
            color: #000000 !important; /* 검정색 글자 */
            font-weight: 700 !important;
            caret-color: #000 !important;
        }
        div[data-testid="stChatInput"] textarea::placeholder {
            color: rgba(0, 0, 0, 0.5) !important; /* 플레이스홀더 명도 확보 */
        }
        div[data-testid="stChatInput"] button {
            background-color: #000 !important;
            border-radius: 50% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Use a high-quality placeholder or the generated image path (absolute for local)
    # Since we are in a task, we will refer to the generated image which will be moved to assets soon.
    ceo_img_url = "https://img.freepik.com/premium-photo/futuristic-banana-ai-assistant-mascot-cyberpunk-style_899449-30504.jpg" 

    st.markdown(
        f"""
        <div class="premium-header">
          <img src="{ceo_img_url}" class="ceo-avatar">
          <div class="header-content">
            <h1>{COMPANY['name']}</h1>
            <p>🏅 {COMPANY['agent']} | AI Vibe Coding 영업 시스템 v4.7 (업데이트완료)</p>
            <div class="header-info">
              <span>📞 {COMPANY['tel']}</span>
              <span>📍 {COMPANY['addr']}</span>
            </div>
            <div style="margin-top:8px; font-size:13px;">
              <a href="https://lotte-ai-app.streamlit.app" target="_blank" style="color:#d4af37; text-decoration:none; font-weight:700;">
                🌐 앱 : https://lotte-ai-app.streamlit.app
              </a>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
