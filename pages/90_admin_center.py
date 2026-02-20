# pages/90_admin_center.py
import streamlit as st
from services.admin_gate import require_admin
import time
import random

# 관리자 인증 (필수)
st.set_page_config(page_title="BARA AI 관리자 센터", page_icon="⚙️", layout="wide")

require_admin()

st.title("⚙️ BARA AI 관리자 센터")
st.caption("Creating Real Estate Intelligence - 매물 관리, 광고 생성, 시스템 설정")

# 상단 대시보드 지표
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 등록 매물", "1,240건", "+12")
col2.metric("AI 매칭 대기", "58건", "-5")
col3.metric("오늘 예약", "12건", "+3")
col4.metric("월 예상 매출", "4,200만원", "+15%")

st.divider()

# 메인 탭 구성
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📢 자동 홍보 생성", "👥 회원/인증 관리", "🤖 AI 모델 모니터링", "📱 알림톡/링크 테스트", "🛠️ 시스템 레거시"])

# --- 탭 1: 자동 홍보 생성 (핵심 기능) ---
with tab1:
    st.subheader("📢 AI 자동 광고 콘텐츠 생성")
    st.info("매물 ID나 정보를 입력하면 숏츠 대본, 블로그 글, SNS 해시태그를 3분 안에 생성합니다.")
    
    col_input, col_preview = st.columns([1, 1])
    
    with col_input:
        with st.form("ad_gen_form"):
            prop_name = st.text_input("매물명 (예: 래미안대치팰리스 34평)")
            prop_price = st.text_input("가격 (예: 매매 32억)")
            prop_feat = st.text_area("매물 특징 (키워드)", "로얄동, 풀옵션, 대치역 3분, 학군 최상")
            prop_img = st.file_uploader("매물 사진 (대표 이미지)", type=["jpg", "png", "jpeg"])
            
            # 법적 필수 표기 사항 체크
            st.markdown("##### ✅ 법적 필수 표기 자동 체크")
            st.checkbox("중개보수 요율 명시 포함", value=True)
            st.checkbox("관리비 세부 내역 포함 (월 평균 등)", value=True)
            st.checkbox("건축물대장 정보(용도, 승인일) 포함", value=True)
            
            gen_btn = st.form_submit_button("✨ AI 콘텐츠 생성하기", type="primary", use_container_width=True)

    with col_preview:
        if gen_btn:
            with st.spinner("AI가 매물을 분석하고 광고를 생성 중입니다..."):
                time.sleep(2) # 시뮬레이션
                st.success("생성 완료!")
                
                # 가상 결과물
                st.markdown("### 🎬 숏츠(Shorts) 대본")
                st.code(f"""
[화면: {prop_name} 전경]
(빠른 배경음악)
자막: 대치동 학군 끝판왕! {prop_name}

[화면: 거실 사진]
내레이션: "34평형 로얄동 등장! {prop_feat}을 갖춘 완벽한 매물입니다."

[화면: 가격 정보]
자막: 매매가 {prop_price} / AI 저평가 점수 92점!

[화면: BARA AI 로고]
내레이션: "지금 바라 AI에서 예약하세요!"
                """, language="text")
                
                st.markdown("### 📝 블로그/SNS 문구")
                st.text_area("결과", 
f"""[강남/대치] {prop_name} 급매물! 학군 수요 최고!
#{prop_name} #{prop_price} #대치동아파트 #학군지

안녕하세요, BARA AI 공인중개사입니다.
오늘 소개할 매물은 {prop_name}입니다.

✅ 가격: {prop_price}
✅ 특징: {prop_feat}
✅ 관리비: 월 평균 25만원 (전기/수도 포함, 규약에 따름)

AI 분석 결과 시세 대비 저평가 구간에 진입했습니다.
지금 바로 아래 링크에서 상세 리포트를 확인하세요!
👉 [앱 링크]""", height=200)

# --- 탭 2: 회원/인증 관리 (핸드폰 인증 시뮬레이션) ---
with tab2:
    st.subheader("👥 회원 및 인증 관리")
    
    st.markdown("#### 📱 휴대폰 본인확인 내역 (최근 5건)")
    
    # 가상 데이터
    auth_data = [
        {"시간": "14:20:05", "번호": "010-****-1234", "이름": "김*수", "상태": "✅ 인증성공", "구분": "매수예약"},
        {"시간": "14:15:22", "번호": "010-****-5678", "이름": "이*영", "상태": "✅ 인증성공", "구분": "매물등록"},
        {"시간": "14:10:11", "번호": "010-****-9876", "이름": "박*준", "상태": "❌ 인증실패", "구분": "로그인"},
    ]
    st.dataframe(auth_data, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### 🔐 관리자 계정 보안 설정")
    st.toggle("2단계 인증(2FA) 강제 적용", value=True)
    st.toggle("해외 IP 접속 차단", value=True)

# --- 탭 3: AI 모델 모니터링 ---
with tab3:
    st.subheader("🤖 AI 모델 성능 지표")
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown("##### 📉 저평가 예측 모델 (MAE)")
        st.line_chart([350, 340, 335, 320, 315, 320, 310]) # 가상 데이터
        st.caption("최근 7일간 오차율 감소 추세 (단위: 만원)")
        
    with m_col2:
        st.markdown("##### 🤝 매칭 성사율 (%)")
        st.bar_chart([15, 18, 20, 22, 25, 24, 28])
        st.caption("AI 추천 매칭 후 실제 예약 전환율")

# --- 탭 4: 알림톡/링크 테스트 ---
with tab4:
    st.subheader("📱 카카오 알림톡 테스트 (앱 링크 발송)")
    st.info("관리자 본인의 휴대폰으로 '검수 요청' 템플릿을 이용해 앱 실행 링크를 보냅니다.")
    
    # 설정값 확인
    try:
        from services.kakao_bizmsg import _cfg, notify_review_requested
        cfg = _cfg()
        is_ready = bool(cfg.get("client_id") and cfg.get("template_review"))
    except ImportError:
        is_ready = False
        def notify_review_requested(a,b,c,d): return None

    if not is_ready:
        st.error("⚠️ secrets.toml에 [kakao_bizmsg] 설정이 누락되었거나 불완전합니다.")
    else:
        with st.form("kakao_test_form"):
            c1, c2 = st.columns(2)
            with c1:
                test_phone = st.text_input("수신자 번호 (- 없이)", placeholder="01012345678")
            with c2:
                # 기본값으로 현재 앱 도메인 추정치 입력
                test_url = st.text_input("보낼 링크 (앱 주소)", value="https://lotte-ai-app.streamlit.app")
            
            send_btn = st.form_submit_button("🚀 내 폰으로 링크 보내기")
        
        if send_btn:
            if not test_phone:
                st.warning("전화번호를 입력하세요.")
            else:
                try:
                    # 검수 요청 템플릿 활용
                    res = notify_review_requested(
                        admin_phone=test_phone,
                        property_id="LINK-TEST",
                        supplier_id="관리자(나)",
                        landing_url=test_url
                    )
                    if res and res.get("code") == "success": 
                        st.success(f"전송 성공! ({test_phone})")
                        st.json(res)
                    else:
                        st.error("전송 실패 (API 응답 확인)")
                        st.json(res)
                except Exception as e:
                    st.error(f"오류 발생: {e}")

# --- 탭 5: 시스템 레거시 ---
with tab5:
    st.subheader("🛠️ 레거시 시스템 바로가기")
    st.warning("경고: 레거시 페이지는 구버전 호환성을 위해서만 사용하십시오.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.page_link("pages/admin.py", label="📎 (구) admin.py 실행", use_container_width=True)
    with c2:
        st.page_link("pages/9_MLOps_Dashboard_Admin.py", label="📎 (구) MLOps 대시보드", use_container_width=True)
    with c3:
        st.page_link("pages/sales_system.py", label="📎 (구) 영업 시스템", use_container_width=True)

st.divider()
st.caption("BARA AI Admin System v2.0 | 보안 등급: 1등급 (Top Secret)")
