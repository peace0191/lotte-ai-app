import streamlit as st

def brand_header(title: str, subtitle: str = "", key_message: str = "",
                 highlight_badges=None, cta_links=None):
    highlight_badges = highlight_badges or []
    cta_links = cta_links or []

    st.markdown("""
    <style>
    .brand-wrap{border:1px solid rgba(255,255,255,.10); border-radius:16px;
      padding:18px 18px; background:rgba(255,255,255,.03);
      box-shadow: 0 10px 30px rgba(0,0,0,.25);}
    .brand-title{font-size:1.4rem; font-weight:900; margin:0 0 6px 0;}
    .brand-sub{opacity:.85; margin:0 0 10px 0;}
    .brand-msg{opacity:.92; margin:10px 0 0 0;}
    .badge-row{display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;}
    .badge{padding:6px 10px; border-radius:999px; font-size:.85rem;
      background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10);}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="brand-wrap">
      <div class="brand-title">{title}</div>
      <div class="brand-sub">{subtitle}</div>
      <div class="brand-msg">{key_message}</div>
      <div class="badge-row">
        {''.join([f'<span class="badge">{b}</span>' for b in highlight_badges])}
      </div>
    </div>
    """, unsafe_allow_html=True)

    if cta_links:
        cols = st.columns(len(cta_links))
        for i,(label, page) in enumerate(cta_links):
            with cols[i]:
                try:
                    st.page_link(page, label=label, use_container_width=True)
                except Exception:
                    st.button(label, use_container_width=True, disabled=True)
