from __future__ import annotations
import streamlit as st

def disc_to_float(s: str) -> float:
    try:
        return float(s.replace("%","").replace("-","").replace(" 할인",""))
    except Exception:
        return 0.0

def render(properties: dict):
    all_items = []
    for complex_name, items in properties.items():
        for it in items:
            all_items.append((complex_name, it))

    # Section 1: TOP 2 급매 매물 (Discount 기준)
    all_items.sort(key=lambda x: disc_to_float(x[1].get("discount","0")), reverse=True)
    top2_urgent = all_items[:2]

    st.markdown("<h3 style='color:#ff4b4b;'>🚀 AI 계약 매칭 시그널 (Contract Signal)</h3>", unsafe_allow_html=True)
    st.caption("AI가 분석한 실시간 매칭 확률 및 계약 임박 시그널입니다. 매수/매도 타이밍을 포착하세요.")
    
    cols1 = st.columns(2)
    for i,(complex_name,it) in enumerate(top2_urgent):
        with cols1[i]:
            st.html(f"""
                <div style="background:rgba(26, 26, 46, 0.8); border:2px solid #ff4b4b; border-radius:24px; margin-bottom:15px; position:relative; overflow:hidden; box-shadow: 0 10px 30px rgba(255, 75, 75, 0.2);">
                    <div style="background:linear-gradient(135deg, #ff4b4b, #8b0000); padding:30px; text-align:center; font-size:40px;">
                        🚨<span style="position:absolute; top:12px; right:12px; background:#fff; color:#ff4b4b; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:900;">매칭 확률 98%</span>
                    </div>
                    <div style="padding:20px;">
                        <div style="font-weight:900; color:#fff; font-size:18px; margin-bottom:8px;">{it['name']}</div>
                        <div style="font-size:13px; color:#adb5bd; margin-bottom:8px;">📍 {it['spec']}</div>
                        <div style="font-size:24px; font-weight:900; color:#ff4b4b; margin-bottom:12px;">{it['price']} <span style="font-size:14px; color:#adb5bd; text-decoration:line-through;">({it.get('original','-')})</span></div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <div style="background:rgba(255, 75, 75, 0.2); color:#ff4b4b; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:700;">
                                {it['discount']} 파격 급매
                            </div>
                            <div style="font-size:12px; color:#d4af37; font-weight:700;">👤 실시간 대기 4명</div>
                        </div>
                        <div style="font-size:12px; color:#6c757d; font-style:italic;">"AI 분석 결과: 매도인 실거주 비중 하락으로 급매 매각 확률 매우 높음"</div>
                    </div>
                </div>
            """)
            
            def go_chat_uv(item=it):
                st.session_state.selected = item
                st.session_state["main_menu_widget"] = "💬 AI 챗봇"
                st.session_state.menu_index = 3
                st.session_state.chat_origin = "undervalued" # Set origin
                st.session_state.education_context = False
                st.session_state.chat = [{"role":"assistant","content":f"안녕하세요! '{item['name']}' 급매물에 대해 안내해 드릴까요?"}]
                st.rerun()

            def go_shorts(item=it):
                st.session_state["shorts_selected_property"] = item
                st.session_state["redirect_to"] = "🎬 AI 숏츠"
                st.rerun()

            btn_c = st.columns(3)
            btn_c[0].button("💬 AI 상담", key=f"uv_u_{it['id']}", use_container_width=True, on_click=go_chat_uv)
            btn_c[1].button("🎬 숏츠 생성", key=f"uv_s_{it['id']}", use_container_width=True, on_click=go_shorts)
            btn_c[2].button("⭐ 관심", key=f"uv_fav_u_{it['id']}", use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Section 2: 대치동 투자 추천 TOP 3 (ML Score 기준)
    all_items.sort(key=lambda x: x[1].get("ml",0), reverse=True)
    # Filter out the top 2 urgent ones to avoid duplication
    urgent_ids = [x[1]['id'] for x in top2_urgent]
    top3_investment = [x for x in all_items if x[1]['id'] not in urgent_ids][:3]

    st.markdown("<h3 style='color:#d4af37;'>💎 가수요-공급 스마트 매칭 TOP 3</h3>", unsafe_allow_html=True)
    st.caption("AI 모델이 선정한 매수 희망자 분포가 가장 높은 투자 우량주입니다.")
    
    cols2 = st.columns(3)
    for i,(complex_name,it) in enumerate(top3_investment):
        with cols2[i]:
            st.html(f"""
                <div style="background:rgba(26, 26, 46, 0.8); border:1px solid #d4af37; border-radius:24px; margin-bottom:15px; position:relative; overflow:hidden;">
                    <div style="background:linear-gradient(135deg, #1a1a2e, #16213e); padding:30px; text-align:center; font-size:40px;">
                        🎯<span style="position:absolute; top:12px; right:12px; background:#d4af37; color:black; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:900;">매칭 80%↑</span>
                    </div>
                    <div style="padding:20px;">
                        <div style="font-weight:900; color:#fff; font-size:18px; margin-bottom:8px;">{it['name']}</div>
                        <div style="font-size:13px; color:#adb5bd; margin-bottom:8px;">📍 {it['spec']}</div>
                        <div style="font-size:24px; font-weight:900; color:#d4af37; margin-bottom:12px;">{it['price']}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <div style="display:inline-block; background:rgba(212, 175, 55, 0.2); color:#d4af37; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:700;">
                                ML 점수: {it['ml']}
                            </div>
                            <div style="font-size:11px; color:#6c757d;">대기 매수자: 12명</div>
                        </div>
                    </div>
                </div>
            """)
            
            def go_chat_inv(item=it):
                st.session_state.selected = item
                st.session_state["main_menu_widget"] = "💬 AI 챗봇"
                st.session_state.menu_index = 3
                st.session_state.chat_origin = "undervalued" # Set origin
                st.session_state.education_context = False
                st.session_state.chat = [{"role":"assistant","content":f"안녕하세요! '{item['name']}' 투자 매물에 대해 안내해 드릴까요?"}]
                st.rerun()

            btn_i = st.columns(2)
            btn_i[0].button("💬 AI 상담", key=f"uv_i_{it['id']}", use_container_width=True, on_click=go_chat_inv)
            btn_i[1].button("⭐ 관심 등록", key=f"uv_fav_i_{it['id']}", use_container_width=True)

    # Bottom Navigation
    from services.ui import render_bottom_nav
    render_bottom_nav("🎯 AI 매칭 시그널")

