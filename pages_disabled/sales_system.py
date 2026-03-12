import streamlit as st
from services.auth import require_admin
from services.ui import header, render_bottom_nav
from services.property_forms import render_complete_property_form

# 관리자 인증
require_admin()

def generate_sales_pack(data):
    # 데이터 추출
    complex_name = data.get("complex_name", "")
    size_type = data.get("size_type", "")
    trans_type = data.get("trans_type", "")
    price_info = ""
    
    if trans_type == "매매":
        price_info = f"매매가 {data.get('price_min')}~{data.get('price_max')}억"
    elif trans_type == "전세":
        price_info = f"전세가 {data.get('deposit_min')}~{data.get('deposit_max')}억"
    else:
        price_info = f"보증금 {data.get('deposit_min')}억 / 월 {data.get('monthly_rent')}만원"

    # 키워드 및 특징
    loc_kw = data.get("loc_keyword", "")
    add_feat = data.get("add_feature", "")
    
    # 1. 숏폼 스크립트 생성
    script = f"""[30초 숏폼 스크립트]
0-3초(훅): "{complex_name} {size_type}, {trans_type} 매물! {price_info}의 기회를 놓치지 마세요."
4-8초(핵심): "{loc_kw}의 중심! {add_feat}의 완벽한 컨디션을 자랑합니다."
9-15초(상세): "방 {data.get('rooms')}개, 욕실 {data.get('bathrooms')}개, {data.get('expansion')} 구조! 주차 {data.get('parking')}까지!"
16-22초(신뢰): "관리비 {data.get('maintenance_fee')}만원대, {data.get('build_year')}년 준공의 쾌적함."
23-30초(CTA): "지금 바로 BARA AI 부동산으로 문의하세요. 놓치면 후회합니다!"
"""

    # 2. 네이버 매물 설명
    naver_text = f"""
📢 {complex_name} {size_type} {trans_type} - {loc_kw}

📍 매물 기본 정보
- 단지명: {complex_name}
- 평형/타입: {size_type}
- 거래유형: {trans_type}
- 가격: {price_info}

🏡 상세 정보
- 입주가능일: {data.get('move_in_date')}
- 방/욕실: {data.get('rooms')}개 / {data.get('bathrooms')}개
- 관리비: 월 평균 {data.get('maintenance_fee')}만원 (규약에 따름)
- 주차: {data.get('parking')}
- 준공년도: {data.get('build_year')}년
- 방향: 남향 (거실 기준)

✨ 특장점
- {add_feat}
- {loc_kw}
- 엘리베이터: {data.get('elevator')}
- 확장여부: {data.get('expansion')}

📞 문의: 롯데타워앤강남빌딩부동산중개(주)
"""

    # 3. 상담 시나리오
    consult_text = f"""[고객 상담 시나리오]
상담원: "고객님, 찾으시는 {complex_name} {size_type} 조건에 딱 맞는 매물이 나왔습니다."
상담원: "가격은 {price_info} 선이고요, 입주는 {data.get('move_in_date')}부터 가능합니다."
상담원: "특히 {loc_kw} 장점이 있고, {add_feat} 매물이라 인기가 많습니다."
상담원: "방 {data.get('rooms')}개 구조에 {data.get('expansion')}이라 공간도 넓게 나왔습니다. 언제 보러 오시겠어요?"
"""
    
    # 4. 쇼룸 HTML (간략)
    showroom_html = f"""<div style='padding:20px; border:1px solid #ddd; border-radius:10px;'>
    <h3>{complex_name} {size_type}</h3>
    <p><b>{price_info}</b></p>
    <p>{loc_kw}</p>
    <hr>
    <p>{add_feat}</p>
    </div>"""

    return script, naver_text, consult_text, showroom_html

def render():
    st.set_page_config(page_title="영업팩 생성기", page_icon="🏢", layout="wide")
    
    # Header
    st.markdown("""
        <div style="text-align:center; padding:20px 0;">
            <h1 style="color:#d4af37; font-size:32px; font-weight:900;">🏢 부동산 AI 영업팩 생성기 (Pro)</h1>
            <p style="color:#9fa6b2;">고도화된 매물 정보를 입력하면 마케팅 콘텐츠를 자동으로 생성합니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Unified Property Form ---
    with st.container():
        # property_forms 모듈 사용
        form_data = render_complete_property_form()
        
        st.write("") # spacer
        
        if st.button("🎉 영업팩(광고/스크립트) 생성하기", type="primary", use_container_width=True):
            script, naver, consult, html = generate_sales_pack(form_data)
            
            st.success("✅ 생성 완료! 아래 탭에서 결과물을 확인하세요.")
            
            t1, t2, t3, t4 = st.tabs(["① 숏폼 스크립트", "② 네이버 매물문구", "③ 고객 상담 멘트", "④ 쇼룸 HTML"])
            
            with t1: st.text_area("숏폼 스크립트", script, height=200)
            with t2: st.text_area("네이버 매물 상세", naver, height=300)
            with t3: st.info(consult)
            with t4: st.code(html, language="html")

    render_bottom_nav("🏢 영업팩 생성")

if __name__ == "__main__":
    render()
