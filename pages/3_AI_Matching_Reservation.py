import streamlit as st
import datetime
# [API Client]
from api_client import client

def app():
    st.set_page_config(page_title="프리미엄 예약 매칭", page_icon="📅", layout="wide")

    # CSS (기존 유지)
    st.markdown("""
        <style>
        .property-card { background-color: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; overflow: hidden; transition: all 0.3s ease; }
        .property-card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.12); }
        .card-content { padding: 16px; }
        .card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 4px; }
        .card-price { font-size: 1rem; font-weight: bold; color: #222; }
        .ai-badge { background-color: #FF385C; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 8px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏡 AI 추천 매물 예약 매칭")
    st.markdown("##### 실시간 서버 매물 데이터 조회 및 예약")

    # 필터
    with st.container():
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        region_query = c1.text_input("🔍 지역 검색", "대치동")
        c2.date_input("체크인", datetime.date.today())
        search_trigger = c4.button("검색", use_container_width=True)

    st.divider()

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("매칭된 추천 리스트")
        
        # [API 호출] 매물 리스트 가져오기
        listings = []
        if search_trigger or True: # 기본값 로드
            res = client.get_listings(region=region_query)
            if res:
                listings = res
            else:
                st.info("조건에 맞는 서버 데이터가 없습니다. (샘플 데이터 표시)")
                # API 연결 안될 때 보여줄 가짜 데이터
                listings = [
                    {"id": 1, "complex_name": "은마아파트 (Offline)", "price": 28.0, "area_py": 34, "deal_type": "매매"},
                    {"id": 2, "complex_name": "래미안대치 (Offline)", "price": 45.0, "area_py": 45, "deal_type": "전세"}
                ]

        for p in listings:
             # API 데이터 필드명 매핑
             title = p.get('complex_name', 'Unknown')
             price = p.get('price', 0)
             pid = p.get('id')
             
             st.markdown(f"""
            <div class="property-card">
                <div class="card-content">
                    <span class="ai-badge">AI 추천</span>
                    <div class="card-title">{title}</div>
                    <div class="card-price">{p.get('deal_type', '매매')} {price}억</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
             
             if st.button(f"📅 방문 예약 ({title})", key=f"btn_res_{pid}"):
                 st.session_state['selected_property'] = p

    with col2:
        if 'selected_property' in st.session_state:
            sel = st.session_state['selected_property']
            st.success(f"✅ 선택됨: {sel.get('complex_name')}")
            
            with st.form("reservation_form"):
                st.write("**방문 예약 정보 입력**")
                # 로그인된 사용자 ID가 있다고 가정 (없으면 임시값)
                visit_date = st.date_input("방문 희망일")
                visit_time = st.time_input("방문 희망 시간")
                msg = st.text_area("요청 사항", "실수요자입니다.")
                
                if st.form_submit_button("예약 확정 요청"):
                    # [API 호출] 예약 생성
                    visit_dt_str = f"{visit_date} {visit_time}"
                    payload = {
                        "demand_id": 1, # 임시 사용자 ID
                        "listing_id": sel.get('id'),
                        "visit_at": visit_dt_str,
                        "message": msg
                    }
                    res = client.create_reservation(payload)
                    
                    if res and res.get("ok"):
                        st.success(f"예약 요청이 전송되었습니다! (예약번호: {res.get('reservation_id')})")
                    else:
                        st.error("예약 요청 실패")
        else:
            st.info("👈 왼쪽 리스트에서 매물을 선택하세요.")

if __name__ == "__main__":
    app()
