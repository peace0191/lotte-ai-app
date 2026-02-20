import streamlit as st
import datetime

def render_transaction_inputs():
    """거래 유형별 상세 가격 입력 폼"""
    st.subheader("2. 거래 유형 및 가격 상세 조건")
    
    trans_type = st.radio("거래 유형 선택", ["매매", "전세", "월세(반전세 포함)"], horizontal=True)
    
    data = {"trans_type": trans_type}
    
    if trans_type == "매매":
        c1, c2 = st.columns(2)
        data["price_min"] = c1.number_input("매매가 최소 (억)", min_value=0.0, step=0.1, format="%.1f")
        data["price_max"] = c2.number_input("매매가 최대 (억)", min_value=0.0, step=0.1, format="%.1f")
        
    elif trans_type == "전세":
        c1, c2 = st.columns(2)
        data["deposit_min"] = c1.number_input("보증금 최소 (억)", min_value=0.0, step=0.1, format="%.1f")
        data["deposit_max"] = c2.number_input("보증금 최대 (억)", min_value=0.0, step=0.1, format="%.1f")
        
    else: # 월세
        c1, c2, c3 = st.columns(3)
        data["deposit_min"] = c1.number_input("보증금 최소 (억)", min_value=0.0, step=0.1, format="%.1f")
        data["deposit_max"] = c2.number_input("보증금 최대 (억)", min_value=0.0, step=0.1, format="%.1f")
        data["monthly_rent"] = c3.number_input("월차임 (만원)", min_value=0, step=10)

    return data

def render_detail_options():
    """세부 옵션 입력 폼"""
    st.subheader("3. 세부 옵션")
    
    c1, c2, c3, c4 = st.columns(4)
    move_in_date = c1.date_input("입주 가능 일자", value=datetime.date.today())
    maintenance_fee = c2.number_input("평균 관리비 (만원)", min_value=0, step=1, value=30)
    build_year = c3.number_input("준공년도", min_value=1970, max_value=2030, value=2015)
    parking = c4.selectbox("주차 가능 여부", ["가능 (자주식)", "가능 (기계식)", "불가능", "확인 필요"])
    
    c5, c6, c7, c8 = st.columns(4)
    elevator = c5.radio("엘리베이터", ["유", "무"], horizontal=True)
    expansion = c6.radio("확장 유무", ["확장형", "비확장"], horizontal=True)
    rooms = c7.number_input("방 개수", min_value=1, step=1, value=3)
    bathrooms = c8.number_input("화장실 개수", min_value=1, step=1, value=2)
    
    return {
        "move_in_date": move_in_date,
        "maintenance_fee": maintenance_fee,
        "build_year": build_year,
        "parking": parking,
        "elevator": elevator,
        "expansion": expansion,
        "rooms": rooms,
        "bathrooms": bathrooms
    }

def render_marketing_keywords():
    """AI 마케팅 키워드 입력 폼"""
    st.subheader("4. AI 마케팅 키워드")
    
    c1, c2 = st.columns(2)
    loc_keyword = c1.text_input("학군/입지 키워드", "대치초, 대청중, 학원가 도보 5분")
    add_feature = c2.text_input("추가 특징 (자유 기재)", "주인거주, 올수리, 갭투자 가능")
    
    return {
        "loc_keyword": loc_keyword,
        "add_feature": add_feature
    }

def render_complete_property_form():
    """전체 부동산 입력 폼 렌더링"""
    # 1. 기본 정보 (간단히 통합)
    st.subheader("1. 매물 기본 정보")
    c1, c2 = st.columns(2)
    complex_name = c1.text_input("단지명/매물명", "대치 래미안 팰리스")
    size_type = c2.text_input("평형/타입", "34평 A타입")
    
    # 2~4. 상세 폼
    trans_data = render_transaction_inputs()
    detail_data = render_detail_options()
    marketing_data = render_marketing_keywords()
    
    # 데이터 통합 반환
    return {
        "complex_name": complex_name,
        "size_type": size_type,
        **trans_data,
        **detail_data,
        **marketing_data
    }
