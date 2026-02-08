from __future__ import annotations
import streamlit as st
from services.local_market import local_market_svc
from services.matching_svc import matching_svc
from services.crawler_svc import crawler_svc
from services.ui import render_bottom_nav

# Corporate Branding (v4.30)
BRAND_NAME = "롯데타워앤강남빌딩부동산중개(주) AI 매칭 플랫폼"

def render(properties: dict):
    st.markdown("## 🏠 단지별 추천매물 (AI 큐레이션)")
    st.caption("CEO 나노 바나나가 직접 엄선한 최고의 명품 매물 리스트입니다.")

    st.markdown("---")

    for complex_name, items in properties.items():
        st.markdown(f"""
            <div style="background:rgba(212, 175, 55, 0.1); border-left:5px solid #d4af37; padding:10px 20px; border-radius:4px; margin:30px 0 20px 0;">
                <span style="color:#d4af37; font-weight:900; font-size:18px;">📍 {complex_name}</span>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, item in enumerate(items[:3]):
            with cols[i]:
                # Calculate Decision Score & Risks
                item["district"] = complex_name.split(" ")[0]
                score_data = local_market_svc.calculate_decision_score(item["id"], item)
                score = score_data["score"]
                risks = local_market_svc.get_risk_status(item["district"])
                
                score_color = "#00d1b2" if score >= 80 else "#d4af37" if score >= 60 else "#ff4b4b"
                
                # AI Shorts Matching Widget Mockup
                shorts_html = f"""
                <div style="height:150px; background:linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1541339907198-e08756ebafe3?auto=format&fit=crop&w=400&q=80'); background-size:cover; position:relative; display:flex; align-items:center; justify-content:center; border-radius:15px 15px 0 0;">
                    <div style="background:rgba(212, 175, 55, 0.8); color:white; padding:8px 16px; border-radius:30px; font-weight:900; font-size:11px; cursor:pointer; border:1px solid #fff;">
                        ▶ CEO 정밀 브리핑 영상
                    </div>
                </div>
                """

                st.html(f"""
                <div style="background:rgba(26, 26, 46, 0.9); border:1px solid rgba(255, 255, 255, 0.05); border-radius:20px; margin-bottom:15px; position:relative; overflow:hidden;">
                    {shorts_html}
                    <div style="padding:20px; min-height:400px;">
                        <div style="font-weight:900; color:#fff; font-size:18px; margin-bottom:8px;">{item['name']}</div>
                        <div style="font-size:12px; color:#9fa6b2; margin-bottom:10px;">{item['spec']}</div>
                        <div style="font-size:24px; font-weight:900; color:#d4af37; margin-bottom:15px;">{item['price']}</div>
                        
                        <div style="background:rgba(255,255,255,0.03); padding:10px; border-radius:10px; border:1px solid rgba(255,255,255,0.05); margin-bottom:10px;">
                            <div style="font-size:10px; color:#8b949e; margin-bottom:3px;">AI Landmark 의사결정 점수</div>
                            <div style="font-size:18px; font-weight:900; color:{score_color};">{score} <span style="font-size:10px; color:#8b949e;">/ 100</span></div>
                        </div>
                        
                        <div style="font-size:10px; color:#ff4b4b; font-weight:700; margin-bottom:10px;">⚠️ 리스크: {", ".join(risks[:1])}</div>
                    </div>
                </div>
                """)

                def go_chat_prop(selected_item=item, s=score, r=risks):
                    st.session_state.selected = selected_item
                    st.session_state.selected["current_score"] = s
                    st.session_state.selected["current_risks"] = r
                    st.session_state["redirect_to"] = "💬 AI 챗봇"
                    st.session_state.chat_origin = "properties"
                    st.session_state.chat = [{"role":"assistant","content":f"안녕하세요! '{selected_item['name']}' 매물에 대해 무엇이든 물어보세요. 현재 AI 점수는 {s}점입니다."}]
                    st.rerun()

                def go_shorts(it=item):
                    st.session_state["shorts_selected_property"] = it
                    st.session_state["redirect_to"] = "🎬 AI 숏츠"
                    st.rerun()

                def reg_interest(it_name=item['name']):
                    st.toast(f"⭐ '{it_name}' 관심매물 등록!", icon="✅")

                btn_cols = st.columns(2)
                # Fix: Remove use_column_width/use_container_width
                btn_cols[0].button("💬 AI 상담", key=f"sel_{item['id']}", on_click=go_chat_prop)
                btn_cols[1].button("⭐ 관심 등록", key=f"fav_{item['id']}", on_click=reg_interest)
                
                btn_cols2 = st.columns(2)
                btn_cols2[0].button("📄 AI 리포트", key=f"rep_{item['id']}")
                btn_cols2[1].button("▶️ 영상", key=f"yt_{item['id']}", on_click=go_shorts)

    # Bottom Navigation
    render_bottom_nav("🏠 추천매물")
