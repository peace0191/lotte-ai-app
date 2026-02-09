import streamlit as st
import pandas as pd
import time

def app():
    st.set_page_config(page_title="프리미엄 사전 등록", page_icon="✨", layout="centered")

    # 스타일 적용
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            text-align: center;
            font-weight: 700;
            margin-bottom: 20px;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #555;
            text-align: center;
            margin-bottom: 40px;
        }
        .role-card {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
            cursor: pointer;
            border: 2px solid transparent;
        }
        .role-card:hover {
            transform: translateY(-5px);
            border-color: #1E3A8A;
        }
        .role-icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 50px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-header'>AI 부동산 매칭 사전 등록</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>인공지능이 당신에게 딱 맞는 집과 고객을 찾아드립니다.<br>지금 등록하고 상위 1%의 매칭 서비스를 경험하세요.</div>", unsafe_allow_html=True)

    if 'role' not in st.session_state:
        st.session_state['role'] = None

    if st.session_state['role'] is None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='role-card'>
                <div class='role-icon'>🏠</div>
                <h3>집을 구해요 (수요자)</h3>
                <p>원하는 조건의 매물을 AI가 분석하여 추천해드립니다.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("수요자로 등록하기"):
                st.session_state['role'] = 'buyer'
                st.rerun()

        with col2:
            st.markdown("""
            <div class='role-card'>
                <div class='role-icon'>🔑</div>
                <h3>집을 내놓아요 (공급자)</h3>
                <p>가장 빠르게, 제값 받고 팔 수 있도록 고객을 찾아드립니다.</p>
            </div>
            """, unsafe_allow_html=True)
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
                type_pref = st.multiselect("선호 유형", ["아파트", "주상복합", "오피스텔", "재건축"])
                
                lifestyle = st.text_area("라이프스타일 및 요구사항 (AI 매칭용)", 
                                       placeholder="예: 초등학생 자녀가 있어서 학원가와 가까워야 하고, 남향을 선호합니다. 조용한 단지를 원해요.")
                
                submitted = st.form_submit_button("AI 매칭 시작하기")
                
                if submitted:
                    with st.spinner("AI가 고객님의 성향을 분석 중입니다..."):
                        time.sleep(2)
                    st.success(f"{name}님, 등록이 완료되었습니다! 3일 내에 맞춤 매물 리포트를 보내드립니다.")
                    st.balloons()

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
                
                features = st.text_area("매물 특징 (AI 숏츠 생성용)",
                                      placeholder="예: 올수리 확장형, 한티역 3분 거리, 대치초 배정, 채광 좋음, 급매")
                
                images = st.file_uploader("매물 사진 업로드 (AI 분석용)", accept_multiple_files=True)
                
                submitted = st.form_submit_button("매물 등록 및 AI 홍보 시작")
                
                if submitted:
                    with st.spinner("이미지 분석 및 AI 숏츠 대본 생성 중..."):
                        time.sleep(2.5)
                    st.success(f"{name}님, 매물이 등록되었습니다! AI가 제작한 홍보 영상을 곧 확인하실 수 있습니다.")
                    st.markdown("### 🎬 AI 자동 생성 예상 숏츠 대본")
                    st.code(f"""
[Intro] 대치동 학군지, 이 가격 실화? {address} 급매!
[Scene 1] 현관을 열자마자 쏟아지는 채광, 올수리된 거실!
[Scene 2] 한티역 도보 3분! 학원가 라이딩 해방!
[Outro] 지금 바로 문의하세요. {price}억, 놓치면 후회합니다.
                    """)

if __name__ == "__main__":
    app()
