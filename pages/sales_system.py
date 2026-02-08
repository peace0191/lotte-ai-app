import streamlit as st
import random
import os
from services.ui import header, render_bottom_nav

def require_admin():
    ADMIN_PIN = "0000"  # PIN Unified
    if st.session_state.get("is_sales_admin"):
        return True

    header() # Show header for consistent UI
    
    st.warning("🔐 관리자 전용 접근")
    st.caption("이 페이지는 관계자 외 접근이 제한됩니다.")
    
    with st.form("sales_admin_login"):
        pin = st.text_input("관리자 PIN 번호를 입력하세요", type="password", placeholder="PIN", help="기본값: 0000")
        if st.form_submit_button("확인"):
            if pin == ADMIN_PIN:
                st.session_state["is_sales_admin"] = True
                st.rerun()
            else:
                st.error("⛔ PIN 번호 오류: 접근이 승인되지 않았습니다.")
    st.stop() # Stop rendering the rest of the page

def generate_sales_pack(data):
    # Data extraction
    complex_name = data.get("complex_name", "")
    size_type = data.get("size_type", "")
    trans_type = data.get("trans_type", "")
    keywords = [k for k in [data.get("k1"), data.get("k2"), data.get("k3")] if k]
    tone = data.get("tone", "표준")
    score = data.get("score", 0)
    ai_comment = data.get("ai_comment", "")
    
    video_url = data.get("video_url", "")
    # Normalize Video URL for Embed
    if "shorts/" in video_url:
        video_url = video_url.replace("shorts/", "watch?v=")
    if "youtu.be/" in video_url:
        video_id = video_url.split("youtu.be/")[1].split("?")[0]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
    manager = data.get("manager", "")
    phone = data.get("phone", "")

    # 1. Shorts Script
    script = f"""[30초 숏폼 스크립트] - {tone} 톤

0-3초(훅):
"이 집, 그냥 {trans_type} 매물이 아닙니다. {complex_name} {size_type}의 진가를 확인하세요."

4-8초(핵심):
"{keywords[0]}와/과 {keywords[1]}을 동시에 잡은 희소 매물! AI 분석 점수 {score}점의 가치."

9-15초(가치):
"특히 {ai_comment if ai_comment else '이 단지만의 특별한 입지와 컨디션을 자랑합니다.'}"
"{keywords[2]}까지 완벽하니 망설일 시간이 없습니다."

16-22초(신뢰):
"{manager}가 자신 있게 추천합니다. 실패 없는 선택, 지금 바로 문의하세요."

23-30초(CTA):
"더 늦기 전에 연락주세요. {phone}"
"""

    # 2. Naver Listing Text
    naver_text = f"""[네이버 부동산 매물 설명]

📢 {complex_name} {size_type} {trans_type} - {keywords[0]} 특급 매물

📍 매물 특징
- {keywords[0]} 최우수 입지
- {keywords[1]} 및 {keywords[2]} 장점 보유
- AI 데이터 분석 매력도: {score}점 (상위 1% 매물)

🏗 단지 정보
- 단지명: {complex_name}
- 평형: {size_type}
- 거래유형: {trans_type}

📝 전문가 한마디
"{ai_comment if ai_comment else '수요가 많은 인기 타입으로 빠른 계약이 예상됩니다.'}"

📞 문의
{manager}
{phone}
*롯데타워앤강남빌딩부동산중개(주)*
"""

    # 3. Consultation Script
    consult_text = f"""[고객 상담 시나리오]

👨‍💼 (상담 도입):
"안녕하세요, 고객님. 찾으시는 {complex_name} {size_type} 매물 마침 좋은 게 나와서 연락드렸습니다."

📊 (데이터 기반 설득):
"저희 AI 시스템 분석 결과, 이 매물은 투자가치 {score}점으로 평가되었습니다. 특히 {keywords[0]} 측면에서 매우 우수하며, {keywords[1]}까지 갖춘 {keywords[2]} 매물이라 고객님 조건에 딱 맞습니다."

💡 (클로징):
"{ai_comment if ai_comment else '현재 대기 수요가 있어 금방 나갈 수 있는 물건입니다.'} 주말 전에 한번 보시는 게 좋겠습니다. 시간 언제가 괜찮으신가요?"
"""

    # 4. Showroom HTML
    showroom_html = f"""
<div style="border:1px solid #ddd; padding:20px; border-radius:10px; font-family:sans-serif;">
    <h2 style="color:#d4af37;">{complex_name} 프리미엄 룸투어</h2>
    <div style="position:relative; padding-bottom:56.25%; height:0; overflow:hidden; max-width:100%;">
        <iframe src="{video_url.replace('watch?v=', 'embed/')}" 
                style="position:absolute; top:0; left:0; width:100%; height:100%;" 
                frameborder="0" allowfullscreen></iframe>
    </div>
    <div style="margin-top:20px;">
        <p><b>{size_type} | {trans_type} | {keywords[0]}</b></p>
        <p>{ai_comment}</p>
        <hr>
        <p style="color:#666; font-size:12px;">문의: {manager} ({phone})</p>
    </div>
</div>
"""
    return script, naver_text, consult_text, showroom_html

def render():
    require_admin()
    header()
    
    st.markdown("""
        <div style="text-align:center; padding:20px 0;">
            <h1 style="color:#d4af37; font-size:32px; font-weight:900;">🏢 부동산 AI 영업팩 생성기 (자동화)</h1>
            <p style="color:#9fa6b2;">버튼 하나로 숏폼 스크립트 / 네이버 매물 문구 / 상담 멘트 / 쇼룸 HTML을 즉시 생성합니다.<br>
            (유튜브 쇼츠 링크 자동 변환 및 백업 시스템 적용)</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("#### 👇 매물 기본 정보를 입력하세요")
        with st.expander("📍 매물 기본 정보", expanded=True):
            c1, c2, c3 = st.columns(3)
            complex_name = c1.text_input("단지명/건물명", "대치 SK VIEW")
            size_type = c2.text_input("평형/타입", "26평")
            trans_type = c3.selectbox("거래 유형", ["임대", "매매", "단기임대"], 0)
        
        with st.expander("🔑 핵심 키워드 & 톤", expanded=True):
            k1, k2, k3 = st.columns(3)
            kw1 = k1.text_input("키워드 1", "학군")
            kw2 = k2.text_input("키워드 2", "동선/평면")
            kw3 = k3.text_input("키워드 3", "희소성")
            tone = st.selectbox("문구 톤 설정", ["표준", "전문적인(Professional)", "친근한(Friendly)", "긴급(Urgent)"], 0)
        
        with st.expander("🧠 AI 분석 데이터 (선택)", expanded=False):
            s1, s2 = st.columns([1, 2])
            score = s1.number_input("매수 매력도(점)", value=92, step=1, max_value=100)
            comment = s2.text_area("AI 분석 코멘트", "학군 수요가 꾸준하며, 최근 전세가 상승세로 인해 갭투자 및 실거주 가치가 모두 높음.")
            
        with st.expander("🎥 영상 및 연락처", expanded=False):
            v1, v2 = st.columns(2)
            # Default placeholder video
            main_vid = v1.text_input("메인 영상(쇼츠/ID/일반URL)", "https://www.youtube.com/shorts/t3M7jLpE9h0") 
            sub_vid = v2.text_input("백업 영상(선택)", "")
            
            m1, m2 = st.columns(2)
            mgr = m1.text_input("담당자", "롯데타워앤강남빌딩부동산중개(주) 이상수")
            ph = m2.text_input("전화", "02-578-8285 / 010-8985-8945")

        if st.button("🎉 생성 완료! 결과 보기", type="primary", use_container_width=True):
            data = {
                "complex_name": complex_name,
                "size_type": size_type,
                "trans_type": trans_type,
                "k1": kw1, "k2": kw2, "k3": kw3,
                "tone": tone,
                "score": score,
                "ai_comment": comment,
                "video_url": main_vid,
                "manager": mgr,
                "phone": ph
            }
            
            res_script, res_naver, res_consult, res_html = generate_sales_pack(data)
            
            st.success("✅ 생성 완료! 아래 결과물을 바로 사용하세요.")
            
            tab1, tab2, tab3, tab4 = st.tabs(["① 숏폼 스크립트", "② 네이버 매물문구", "③ 고객 상담 멘트", "④ 쇼룸 HTML"])
            
            with tab1:
                st.markdown("##### 30초 숏폼 스크립트")
                st.code(res_script, language="text")
                st.caption("💡 팁: 이 스크립트를 Vrew나 CapCut에 붙여넣으면 AI 음성과 자막이 자동 생성됩니다.")
                
            with tab2:
                st.markdown("##### 네이버/블로그 업로드용 매물 설명")
                st.code(res_naver, language="text")
                st.button("📋 복사하기 (클립보드)", key="copy_naver")
                
            with tab3:
                st.markdown("##### 전화/대면 상담 시나리오")
                st.info(res_consult)
                
            with tab4:
                st.markdown("##### 자사몰/블로그용 쇼룸 임베드 코드")
                st.code(res_html, language="html")
                st.markdown("▼ 미리보기")
                st.components.v1.html(res_html, height=400, scrolling=True)

    # Bottom Navigation
    render_bottom_nav("🏢 영업팩 생성")
