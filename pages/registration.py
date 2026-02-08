import streamlit as st
import time
from services.ui import header, render_bottom_nav

def render():
    header()
    
    st.markdown("""
        <div style="text-align:center; padding:20px 0;">
            <h1 style="color:#d4af37; font-size:32px; font-weight:900;">🚀 롯데타워 AI 사전 매칭 센터</h1>
            <p style="color:#9fa6b2;">에어비앤비 방식의 스마트 예약 시스템으로 매칭 확률을 300% 높이세요.</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏠 1. 공급자(임대/매도) 등록", "🔑 2. 수요자(임차/매수) 등록"])

    with tab1:
        st.markdown("""
            <div style="background:rgba(212,175,55,0.05); border:1px solid #d4af37; border-radius:15px; padding:30px; margin-bottom:20px;">
                <h3 style="color:#fff; margin-top:0;">🛡️ 내 집의 골든타임 예약 (공급)</h3>
                <p style="font-size:14px; color:#adb5bd;">AI가 주변 실거래와 학원가 입지 데이터를 분석하여 가장 비싸게 거래될 시점에 마케팅을 시작합니다.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("supply_form"):
            col1, col2 = st.columns(2)
            complex_name = col1.selectbox("대상 단지", ["래미안대치팰리스", "대치SK뷰", "대치아이파크", "대치은마", "시그니엘"])
            dong_ho = col2.text_input("동/호수 (비공개 보안 유지)", placeholder="예: 101동 1502호")
            
            p1, p2 = st.columns(2)
            hope_price = p1.number_input("희망 가격 (억 단위)", value=30, step=1)
            available_date = p2.date_input("매물 인도 가능일")
            
            st.markdown("---")
            st.markdown("#### 🎁 AI 공급자 패키지 (체크 시 자동 수행)")
            s_opt1 = st.checkbox("나노 바나나 CEO AI 숏츠 제작 및 배포", value=True)
            s_opt2 = st.checkbox("주변 단지 대비 저평가 분석 리포트 생성", value=True)
            s_opt3 = st.checkbox("VIP 대기 수요자(4,200명) 우선 매칭 알림", value=True)
            
            if st.form_submit_button("🚀 AI 마케팅 및 매칭 예약 완료"):
                with st.spinner("MLOps 파이프라인이 유동성 및 매칭 확률 분석 중..."):
                    time.sleep(2)
                    st.success("✅ 등록 완료! 현재 대기 수요자 데이터와 대조한 결과입니다.")
                    
                    st.markdown("""
                        <div style="background:rgba(212, 175, 55, 0.1); border:2px solid #d4af37; border-radius:15px; padding:20px; text-align:center;">
                            <div style="font-size:14px; color:#d4af37;">AI 기반 계약 매칭 예상 점수</div>
                            <div style="font-size:48px; font-weight:900; color:#d4af37;">94 / 100</div>
                            <p style="font-size:13px; color:#adb5bd; margin-top:10px;">
                                🤖 <b>AI 코칭:</b> 현재 대치동 학원가 인근 수요가 급증하고 있어, <br>
                                등록하신 가격대는 <b>'1주일 내 계약'</b> 확률이 매우 높습니다. <br>
                                <b>나노 바나나 CEO 숏츠 제작</b>을 즉시 시작합니다!
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()

    with tab2:
        st.markdown("""
            <div style="background:rgba(74,144,226,0.05); border:1px solid #4A90E2; border-radius:15px; padding:30px; margin-bottom:20px;">
                <h3 style="color:#fff; margin-top:0;">🎯 VIP 입주 희망 대기 (수요)</h3>
                <p style="font-size:14px; color:#adb5bd;">비공개 급매물이나 퇴거 예정 매물을 일반 포털보다 48시간 먼저 선점하세요.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("demand_form"):
            col1 = st.columns(1)[0]
            target_complex = col1.multiselect("선호 단지 (복수 선택)", ["래미안대치팰리스", "대치SK뷰", "대치아이파크", "대치은마", "시그니엘"], default=["래미안대치팰리스"])
            
            p1, p2 = st.columns(2)
            pref_size = p1.multiselect("선호 평형대", ["20평대", "30평대", "40평대", "50평대 이상", "펜트하우스"], default=["30평대"])
            pref_rooms = p2.selectbox("희망 방 개수", ["방 2개", "방 3개", "방 4개 이상"], index=1)
            
            st.markdown("#### 💰 예산 (Budget)")
            b1, b2, b3 = st.columns(3)
            min_budget = b1.number_input("최소 예산 (억)", value=20, step=1, min_value=1)
            max_budget = b2.number_input("최대 예산 (억)", value=30, step=1, max_value=100)
            monthly_rent = b3.number_input("희망 월차임 (만원, 전세시 0)", value=0, step=10, help="반전세/월세 희망 시 최대 월 부담 가능액")
            
            f1, f2 = st.columns(2)
            edu_priority = f1.selectbox("가장 중요한 교육 여건", ["대치초 근접", "학원가 도보 1분", "대청중 배정", "단대부고 인근"])
            move_period = f2.selectbox("희망 입주 시기", ["3개월 내", "6개월 내", "방학 시즌", "상시 대기"])
            
            st.markdown("---")
            st.markdown("#### 🔔 개인화 마케팅 수신 설정")
            d_opt1 = st.checkbox("나노 바나나 CEO의 일일 급매 브리핑 영상 수신", value=True)
            d_opt2 = st.checkbox("관심 단지 저평가 시그널(ML Score 90↑) 카톡 알림", value=True)
            
            st.markdown("""
                <style>
                /* Style only the form submit button inside this specific form context if possible, or generally primary buttons in forms */
                button[kind="primaryFormSubmit"] {
                    background-color: #008000 !important;
                    color: white !important; 
                    font-size: 20px !important;
                    font-weight: bold !important;
                    padding: 12px !important;
                    border: 0px !important;
                }
                button[kind="primaryFormSubmit"]:hover {
                    background-color: #006400 !important;
                    color: #fff !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("💎 대치동 VIP 매칭 대기열 합류 물건 클릭해 보기", type="primary", use_container_width=True)

        if submitted:
            with st.spinner("가용 매물 및 MLOps 데이터와 실시간 매칭 중..."):
                time.sleep(2)
                st.markdown(f"""
                    <div style="background:rgba(74, 144, 226, 0.1); border:2px solid #4A90E2; border-radius:15px; padding:20px; text-align:center;">
                        <div style="font-size:14px; color:#4A90E2;">🚀 실시간 입주 대기 매칭 분석 서비스</div>
                        <div style="display:flex; justify-content:space-around; align-items:center; margin:20px 0;">
                            <div>
                                <div style="font-size:11px; color:#9fa6b2;">VIP 대기 순번</div>
                                <div style="font-size:24px; font-weight:900; color:#fff;">4 <span style="font-size:14px;">위</span></div>
                            </div>
                            <div style="width:1px; height:40px; background:rgba(255,255,255,0.1);"></div>
                            <div>
                                <div style="font-size:11px; color:#9fa6b2;">실시간 매칭률</div>
                                <div style="font-size:24px; font-weight:900; color:#4A90E2;">92 <span style="font-size:14px;">%</span></div>
                            </div>
                        </div>
                        <p style="font-size:13px; color:#eaeef6; margin-top:10px;">
                            🛡️ <b>나노 바나나의 조언:</b> 설정하신 예산 {min_budget}~{max_budget}억 범위 내 매물이 현재 2건 발견되었습니다. <br>
                            다른 대기자보다 먼저 <b>'급매 시그널'</b>을 받으시려면 카톡 알림을 유지해 주세요.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("")
                if st.button("🔽 가장 근접한 추천 매물 바로보기 (AI 매칭)", use_container_width=True):
                     st.session_state["manual_nav_target"] = "🏠 추천매물"
                     st.rerun()

                st.balloons()

    st.markdown("---")
    st.markdown("""
        <div style="background:#1a1a1a; padding:20px; border-radius:10px; text-align:center;">
            <p style="font-size:12px; color:#666;">본 시스템은 Fast Campus MLOps 파이프라인(MLflow, Airflow)을 통해 실시간으로 데이터를 검증하고 있습니다.</p>
        </div>
    """, unsafe_allow_html=True)

    # Bottom Navigation
    render_bottom_nav("🚀 사전등록 매칭")
