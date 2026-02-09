import streamlit as st
import datetime

def app():
    st.set_page_config(page_title="프리미엄 예약 매칭", page_icon="📅", layout="wide")

    # CSS for Airbnb style card
    st.markdown("""
        <style>
        .property-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        .property-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        }
        .card-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background-color: #ddd;
        }
        .card-content {
            padding: 16px;
        }
        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .card-price {
            font-size: 1rem;
            font-weight: bold;
            color: #222;
        }
        .card-meta {
            font-size: 0.9rem;
            color: #717171;
            margin-bottom: 8px;
        }
        .ai-badge {
            background-color: #FF385C;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏡 AI 추천 매물 예약 매칭")
    st.markdown("##### 고객님의 성향을 분석하여 가장 적합한 1%의 매물을 엄선했습니다.")

    # 필터 섹션 (상단 고정 느낌)
    with st.container():
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        c1.text_input("🔍 지역, 아파트명 검색", "대치동 래미안대치팰리스")
        c2.date_input("체크인", datetime.date.today())
        c3.date_input("체크아웃", datetime.date.today() + datetime.timedelta(days=1))
        c4.button("검색 수정", use_container_width=True)

    st.divider()

    # 결과 표시
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("매칭된 추천 리스트")
        
        # 매물 카드 데이터 (가상)
        properties = [
            {
                "id": 1,
                "title": "래미안대치팰리스 1단지 45평 로얄층",
                "price": "55억",
                "type": "매매",
                "spec": "방 4 · 화장실 2 · 남향",
                "score": 98,
                "img": "https://via.placeholder.com/400x200?text=Apartment+A"
            },
            {
                "id": 2,
                "title": "대치 SK VIEW 34평 급매",
                "price": "32억",
                "type": "매매",
                "spec": "방 3 · 화장실 2 · 초품아",
                "score": 94,
                "img": "https://via.placeholder.com/400x200?text=Apartment+B"
            },
               {
                "id": 3,
                "title": "은마아파트 30평 재건축 투자",
                "price": "24억",
                "type": "매매/투자",
                "spec": "방 3 · 화장실 1 · 투자유망",
                "score": 91,
                "img": "https://via.placeholder.com/400x200?text=Apartment+C"
            }
        ]

        for p in properties:
             st.markdown(f"""
            <div class="property-card">
                <div class="card-content">
                    <span class="ai-badge">AI 매칭 점수 {p['score']}점</span>
                    <div class="card-title">{p['title']}</div>
                    <div class="card-meta">{p['spec']}</div>
                    <div class="card-price">{p['type']} {p['price']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
             c_btn1, c_btn2 = st.columns(2)
             if c_btn1.button(f"📅 방문 예약 ({p['title']})", key=f"btn_reserve_{p['id']}"):
                 st.session_state['selected_property'] = p
             if c_btn2.button(f"💬 챗봇 상담", key=f"btn_chat_{p['id']}"):
                 st.info("AI 챗봇 상담이 시작됩니다 (구현 예정)")

    with col2:
        # 예약 및 지도 화면 (우측 고정 느낌)
        if 'selected_property' in st.session_state:
            sel = st.session_state['selected_property']
            st.success(f"✅ 선택됨: {sel['title']}")
            with st.form("reservation_form"):
                st.write("**방문 예약 정보 입력**")
                st.date_input("방문 희망일")
                st.time_input("방문 희망 시간")
                st.text_area("요청 사항", "아이와 함께 방문합니다.")
                if st.form_submit_button("예약 확정 요청"):
                    st.success("예약 요청이 중개사에게 전송되었습니다! 승인 시 알림을 드립니다.")
        else:
            st.info("👈 왼쪽 리스트에서 매물을 선택하여 예약을 진행하세요.")
            st.markdown("### 🗺️ 위치 확인")
            # 간단한 지도 플레이스홀더
            st.markdown("""
            <div style="background-color:#eee; height:400px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#888;">
                지도 API 연동 영역 (Naver/Kakao Map)
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()
