import streamlit as st
import time
# [API Client] 안전한 통신 모듈 임포트
from api_client import client

def app():
    st.set_page_config(page_title="프리미엄 사전 등록", page_icon="✨", layout="centered")

    # 스타일 적용 (기존 유지)
    st.markdown("""
        <style>
        .main-header { font-size: 2.5rem; color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 20px; }
        .sub-header { font-size: 1.2rem; color: #555; text-align: center; margin-bottom: 40px; }
        .role-card { background-color: #f8f9fa; border-radius: 15px; padding: 30px; 
                     box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; transition: transform 0.3s; 
                     cursor: pointer; border: 2px solid transparent; }
        .role-card:hover { transform: translateY(-5px); border-color: #1E3A8A; }
        .role-icon { font-size: 3rem; margin-bottom: 15px; }
        .stButton>button { width: 100%; border-radius: 8px; height: 50px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-header'>AI 부동산 매칭 사전 등록</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>인공지능이 당신에게 딱 맞는 집과 고객을 찾아드립니다.<br>지금 등록하고 상위 1%의 매칭 서비스를 경험하세요.</div>", unsafe_allow_html=True)

    if 'role' not in st.session_state:
        st.session_state['role'] = None

    if st.session_state['role'] is None:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""<div class='role-card'><div class='role-icon'>🏠</div><h3>집을 구해요 (수요자)</h3><p>AI 맞춤 추천</p></div>""", unsafe_allow_html=True)
            if st.button("수요자로 등록하기"):
                st.session_state['role'] = 'buyer'
                st.rerun()

        with col2:
            st.markdown("""<div class='role-card'><div class='role-icon'>🔑</div><h3>집을 내놓아요 (공급자)</h3><p>AI 마케팅 자동화</p></div>""", unsafe_allow_html=True)
            if st.button("공급자로 등록하기"):
                st.session_state['role'] = 'seller'
                st.rerun()

    else:
        if st.button("← 뒤로 가기"):
            st.session_state['role'] = None
            st.rerun()

        if st.session_state['role'] == 'buyer':
            st.success("🏠 수요자(매수/임차) 사전 등록")
            with st.form("buyer_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("성함")
                    phone = st.text_input("연락처 (010-XXXX-XXXX)")
                with col2:
                    budget = st.slider("예산 범위 (억원)", 10, 200, (30, 80))
                    move_date = st.date_input("입주 희망일")
                
                area_pref = st.multiselect("선호 지역", ["대치동", "도곡동", "역삼동", "개포동", "삼성동"])
                # API 스키마에 맞춰 데이터 구성
                lifestyle = st.text_area("라이프스타일 및 요구사항")
                
                submitted = st.form_submit_button("AI 매칭 시작하기")
                
                if submitted:
                    if not name or not phone:
                        st.error("성함과 연락처는 필수입니다.")
                    else:
                        with st.spinner("AI 서버에 등록 중..."):
                            # [API 호출] 안전하게 데이터 전송
                            payload = {
                                "name": name,
                                "phone": phone,
                                "budget_deposit": float(budget[0]), # 최소 예산
                                "budget_monthly": 0,
                                "area_min": 20, # 임시값
                                "area_max": 60, # 임시값
                                "preferred_regions": ",".join(area_pref),
                                "preferences": {"lifestyle": lifestyle, "budget_max": budget[1]}
                            }
                            res = client.register_demand(payload)
                            
                            if res and res.get("ok"):
                                st.success(f"{name}님, 등록이 완료되었습니다! (ID: {res.get('id')})")
                                st.balloons()
                            else:
                                st.error("등록에 실패했습니다. 잠시 후 다시 시도해주세요.")

        elif st.session_state['role'] == 'seller':
            st.info("🔑 공급자(매도/임대) 사전 등록")
            with st.form("seller_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("성함")
                    phone = st.text_input("연락처")
                with col2:
                    address = st.text_input("매물 주소")
                    price = st.number_input("희망 가격 (억원)", min_value=1.0, step=0.5)
                
                features = st.text_area("매물 특징 (AI 숏츠 생성용)", placeholder="예: 올수리 확장형, 한티역 3분 거리...")
                
                submitted = st.form_submit_button("매물 등록 및 AI 홍보 시작")
                
                if submitted:
                    with st.spinner("서버 전송 및 AI 숏츠 대본 생성 중..."):
                        # [API 호출]
                        payload = {
                            "complex_name": address, # 임시 매핑
                            "address": address,
                            "region": "대치동", # 임시
                            "deal_type": "매매",
                            "price": float(price),
                            "area_py": 34, # 임시
                            "floor": 10, # 임시
                            "features": {"desc": features, "owner_name": name, "owner_phone": phone}
                        }
                        res = client.register_supply(payload)
                        
                        if res and res.get("ok"):
                            st.success(f"{name}님, 매물이 등록되었습니다! AI 마케팅이 시작됩니다.")
                            # 가상 숏츠 대본 표시 (클라이언트 측 데모)
                            st.markdown("### 🎬 AI 자동 생성 예상 숏츠 대본")
                            st.code(f"[Intro] {address} 급매! {price}억 놓치면 후회합니다.")
                        else:
                            st.error("등록 실패")

if __name__ == "__main__":
    app()
