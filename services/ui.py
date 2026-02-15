import streamlit as st

def inject_mobile_ui():
    st.markdown("""
    <style>
      .block-container { padding-top: 1.0rem; padding-bottom: 6.2rem; }
      .card { border:1px solid rgba(255,255,255,.10); border-radius:16px; padding:14px; margin:10px 0; }
      .muted { opacity:.82; }

      /* Sticky CTA Footer */
      .sticky-cta {
        position: fixed; left: 0; right: 0; bottom: 0;
        padding: .85rem 1rem;
        background: rgba(18,18,18,.92);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(255,255,255,.12);
        z-index: 9991; /* Below Streamlit Elements if needed, or higher */
      }
      .sticky-cta .btns { display:flex; gap:.6rem; }
      .sticky-cta a {
        flex:1; text-align:center; padding:.85rem .8rem;
        border-radius: 14px; text-decoration:none; font-weight: 800;
        border:1px solid rgba(255,255,255,.14);
      }
      .cta1 { background:#2d6cdf; color:white; }
      .cta2 { background:#16a34a; color:white; }
      
      /* Hide Standard Footer */
      footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def sticky_cta(apply_anchor="#apply", shorts_anchor="#shorts"):
    st.markdown(f"""
    <div class="sticky-cta">
      <div class="btns">
        <a class="cta1" href="{apply_anchor}">상담/예약</a>
        <a class="cta2" href="{shorts_anchor}">숏츠/홍보</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.title("📍 대치1동 AI 부동산")
        
        st.page_link("pages/01_daechi_info.py", label="🏠 지역정보", icon="🏠")
        st.page_link("pages/02_properties.py", label="⭐ 추천매물", icon="⭐")
        st.page_link("pages/03_ai_matching.py", label="🤖 AI 매칭·챗봇", icon="🤖")
        st.page_link("pages/04_registration.py", label="📝 매물등록/의뢰", icon="📝")
        st.page_link("pages/05_shorts.py", label="🎬 숏츠매물", icon="🎬")
        st.page_link("pages/youtuber_lab.py", label="🧪 YOU-LAB", icon="🧪") # Restored
        st.page_link("pages/undervalued.py", label="🚨 AI 매칭 시그널", icon="🚨") # Restored
        st.page_link("pages/sales_system.py", label="🏢 영업팩 생성", icon="🏢") # Restored/Added as requested

        # role = st.session_state.get("role", "demo")
        # if role == "admin":
        st.markdown("---")
        st.header("관리자 (Demo)")
        st.page_link("pages/90_admin_center.py", label="⚙ 관리자센터", icon="⚙")

# --- Legacy Utilities for Backward Compatibility ---

def header(title="대치1동 AI 부동산", subtitle="롯데타워앤강남빌딩부동산중개(주)"):
    """
    Renders a standard legacy header.
    In new UI, often redundant due to inject_mobile_ui and top titles, but kept for compatibility.
    """
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:10px;">
        <div style="font-size:1.5rem; font-weight:800; color:#fff;">{title}</div>
        <div style="font-size:0.9rem; color:#aaa;">{subtitle}</div>
    </div>
    <hr style="border-top: 1px solid rgba(255,255,255,0.1); margin: 0.5rem 0 1.5rem 0;">
    """, unsafe_allow_html=True)

def scroll_to_top():
    """Jumps to top + slightly refreshes/reruns in some contexts, but mainly JS."""
    js = """
    <script>
        var body = window.parent.document.querySelector(".main");
        if (body) { body.scrollTop = 0; }
    </script>
    """
    st.components.v1.html(js, height=0)

def render_bottom_nav(current_page_label=None):
    """
    Legacy bottom nav. 
    In the new mobile layout, we use 'sticky_cta' for the fixed bottom bar.
    This function is kept to prevent ImportErrors in legacy pages, 
    but we can make it render nothing or a simple spacer to avoid conflict.
    """
    # Simply return or render a spacer.
    # If the user really wants the old buttons, we can render them ABOVE the sticky footer.
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
