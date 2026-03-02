"""
pages/ai_matching_reservation.py
AI 사전 매칭 예약 폼 - 파발마 스타일 상세 폼
있습니다(공급) / 구합니다(수요) 탭 분리
"""
import streamlit as st
import datetime
import time
import json

# ─────────────────────────────────────────────────────────────────────────────
# 공통 상수 정의
# ─────────────────────────────────────────────────────────────────────────────
PROPERTY_TYPES = ["아파트", "빌라/연립", "오피스텔", "상가/상업", "토지", "기타"]
TRADE_TYPES    = ["매매", "전세", "월세(반전세 포함)"]

# 파발마 스타일 특징 체크박스
FEATURES_SUPPLY = [
    "💰 금액조절 가능",
    "👀 바로 볼 수 있는",
    "🏗️ 새로 지은",
    "🙋 손님 대기중",
    "🚇 역세권 위치",
    "🔧 수리 깨끗한",
    "🏦 전세대출 가능",
    "🛋️ 풀옵션",
]
FEATURES_DEMAND = [
    "💰 금액조절 가능",
    "🚀 즉시입주 가능",
    "🚗 주차 필수",
    "🏫 학군 중요",
    "🚇 역세권 선호",
    "🏗️ 신축 선호",
    "🏦 대출 활용 예정",
    "🏠 실거주 목적",
]

# 서울 주요 구/동 목록 (예시)
REGIONS_GU = [
    "강남구", "서초구", "송파구", "강동구", "마포구",
    "용산구", "성동구", "광진구", "강서구", "양천구",
    "영등포구", "동작구", "관악구", "구로구", "금천구",
    "서대문구", "은평구", "종로구", "중구", "노원구",
    "도봉구", "강북구", "성북구", "중랑구", "동대문구",
]

# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼 함수
# ─────────────────────────────────────────────────────────────────────────────
def sqm_to_pyeong(sqm: float) -> float:
    """㎡ → 평 환산 (1평 = 3.3058㎡)"""
    return round(sqm / 3.3058, 2)


def render_price_inputs(trade_type: str, prefix: str = "") -> dict:
    """거래 유형에 따른 동적 가격 입력 필드"""
    data = {}
    if trade_type == "매매":
        col1, col2 = st.columns(2)
        data["매매가_억"] = col1.number_input(
            f"매매가 (억원)", min_value=0.0, step=0.1, format="%.1f", key=f"{prefix}_sale_price"
        )
        data["매매가_만원"] = col2.number_input(
            "   + 만원 단위", min_value=0, step=100, key=f"{prefix}_sale_price_man"
        )
    elif trade_type == "전세":
        col1, col2 = st.columns(2)
        data["보증금_억"] = col1.number_input(
            "보증금 (억원)", min_value=0.0, step=0.1, format="%.1f", key=f"{prefix}_deposit"
        )
        data["보증금_만원"] = col2.number_input(
            "   + 만원 단위", min_value=0, step=100, key=f"{prefix}_deposit_man"
        )
    else:  # 월세
        col1, col2, col3 = st.columns(3)
        data["보증금_억"] = col1.number_input(
            "보증금 (억원)", min_value=0.0, step=0.1, format="%.1f", key=f"{prefix}_monthly_deposit"
        )
        data["보증금_만원"] = col2.number_input(
            "   + 만원 단위", min_value=0, step=100, key=f"{prefix}_monthly_deposit_man"
        )
        data["월세_만원"] = col3.number_input(
            "월세 (만원)", min_value=0, step=5, key=f"{prefix}_monthly_rent"
        )
    return data


def render_area_inputs(prefix: str) -> dict:
    """면적 입력 + ㎡→평 자동환산"""
    st.markdown("##### 📐 면적/규모")
    col1, col2, col3 = st.columns(3)
    supply_sqm = col1.number_input("공급면적 (㎡)", min_value=0.0, step=0.5, format="%.1f", key=f"{prefix}_supply_sqm")
    private_sqm = col2.number_input("전용면적 (㎡)", min_value=0.0, step=0.5, format="%.1f", key=f"{prefix}_private_sqm")
    land_sqm = col3.number_input("대지면적 (㎡)", min_value=0.0, step=0.5, format="%.1f", key=f"{prefix}_land_sqm")

    if supply_sqm > 0 or private_sqm > 0:
        py_cols = st.columns(3)
        if supply_sqm > 0:
            py_cols[0].info(f"≈ **{sqm_to_pyeong(supply_sqm)}평**")
        if private_sqm > 0:
            py_cols[1].info(f"≈ **{sqm_to_pyeong(private_sqm)}평**")
        if land_sqm > 0:
            py_cols[2].info(f"≈ **{sqm_to_pyeong(land_sqm)}평**")

    return {
        "공급면적_㎡": supply_sqm,
        "전용면적_㎡": private_sqm,
        "대지면적_㎡": land_sqm,
        "공급면적_평": sqm_to_pyeong(supply_sqm),
        "전용면적_평": sqm_to_pyeong(private_sqm),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 탭 1: 있습니다(공급자) 폼
# ─────────────────────────────────────────────────────────────────────────────
def render_supply_form():
    st.markdown("#### 🏠 공급 물건 상세 작성 (있습니다)")
    st.caption("보유하고 계신 매물 정보를 상세히 입력해주세요.")
    st.divider()

    # ── 섹션 1: 기본 인적사항 ──────────────────────────────────────────────
    st.markdown("##### 👤 기본 인적사항 (필수)")
    c1, c2 = st.columns(2)
    s_name  = c1.text_input("이름 (중개사명)", placeholder="홍길동 공인중개사", key="s_name")
    s_phone = c2.text_input("연락처", placeholder="010-1234-5678", key="s_phone")

    st.divider()

    # ── 섹션 2: 매물 정보 ─────────────────────────────────────────────────
    st.markdown("##### 🏷️ 매물 종류 & 거래 구분")
    c1, c2 = st.columns(2)
    s_prop_type  = c1.selectbox("매물 종류", PROPERTY_TYPES, key="s_prop_type")
    s_trade_type = c2.radio("거래 구분", TRADE_TYPES, horizontal=True, key="s_trade_type")

    st.divider()

    # ── 섹션 3: 위치 정보 ─────────────────────────────────────────────────
    st.markdown("##### 📍 위치 정보")
    c1, c2 = st.columns(2)
    s_complex = c1.text_input("단지명 / 건물명", placeholder="○○아파트, ○○빌라 등", key="s_complex")
    s_dong_ho = c2.text_input("동/호수", placeholder="예) 101동 1501호", key="s_dong_ho")

    c3, c4, c5 = st.columns(3)
    s_floor       = c3.number_input("해당 층수", min_value=1, max_value=100, value=5, key="s_floor")
    s_total_floor = c4.number_input("총 층수", min_value=1, max_value=200, value=20, key="s_total_floor")
    s_rooms       = c5.number_input("방 수", min_value=1, max_value=20, value=3, key="s_rooms")
    c6, c7 = st.columns(2)
    s_baths = c6.number_input("화장실 수", min_value=1, max_value=10, value=2, key="s_baths")
    s_direction = c7.selectbox("향", ["남향", "남동향", "남서향", "동향", "서향", "북향", "기타"], key="s_direction")

    st.divider()

    # ── 섹션 4: 면적/규모 ─────────────────────────────────────────────────
    s_area = render_area_inputs("s")

    st.divider()

    # ── 섹션 5: 가격 ──────────────────────────────────────────────────────
    st.markdown("##### 💵 가격 정보")
    s_price = render_price_inputs(s_trade_type, prefix="s")

    st.divider()

    # ── 섹션 6: 특징 선택 (파발마 스타일) ────────────────────────────────
    st.markdown("##### ✅ 매물 특징 선택 (해당 사항 모두 체크)")
    s_features = []
    feat_cols = st.columns(4)
    for i, feat in enumerate(FEATURES_SUPPLY):
        if feat_cols[i % 4].checkbox(feat, key=f"s_feat_{i}"):
            s_features.append(feat)

    st.divider()

    # ── 섹션 7: 이사예정일 / 특이사항 ────────────────────────────────────
    st.markdown("##### 📅 일정 & 특이사항")
    c1, c2 = st.columns(2)
    s_move_date = c1.date_input(
        "이사예정일 / 인도가능일",
        value=datetime.date.today() + datetime.timedelta(days=30),
        key="s_move_date"
    )
    s_memo = c2.text_area("특이사항 메모 (자유 기재)", placeholder="예) 세입자 이사 후 즉시 가능, 풀옵션 협의 가능 등", height=100, key="s_memo")

    st.divider()

    # ── 섹션 8: 발송 지역 ────────────────────────────────────────────────
    st.markdown("##### 📡 발송 지역 선택")
    st.caption("이 물건 정보를 발송할 구/지역을 선택해주세요.")
    c1, c2 = st.columns(2)
    s_send_gu = c1.multiselect("발송 구 선택", REGIONS_GU, default=["강남구"], key="s_send_gu")
    s_send_custom = c2.text_input("추가 직접 입력 (동, 지역명 등)", placeholder="예) 대치동, 압구정동", key="s_send_custom")

    # ── 접수 버튼 ────────────────────────────────────────────────────────
    st.divider()
    if st.button("🚀 [있습니다] 공급 물건 접수하기", type="primary", use_container_width=True, key="btn_supply"):
        errors = []
        if not s_name:  errors.append("이름을 입력해주세요.")
        if not s_phone: errors.append("연락처를 입력해주세요.")
        if not s_complex: errors.append("단지명을 입력해주세요.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            submission = {
                "접수유형": "있습니다(공급)",
                "이름": s_name,
                "연락처": s_phone,
                "매물종류": s_prop_type,
                "거래구분": s_trade_type,
                "단지명": s_complex,
                "동호수": s_dong_ho,
                "층수": f"{s_floor}/{s_total_floor}층",
                "방수": s_rooms,
                "화장실수": s_baths,
                "향": s_direction,
                **s_area,
                **s_price,
                "특징": s_features,
                "이사예정일": str(s_move_date),
                "특이사항": s_memo,
                "발송구": s_send_gu,
                "발송지역추가": s_send_custom,
                "접수시각": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            with st.spinner("🔒 보안 서버에 암호화하여 전송 중입니다..."):
                time.sleep(1.2)

            st.success("✅ [있습니다] 공급 물건 접수가 완료되었습니다!")
            st.balloons()
            with st.expander("📊 접수 내용 확인 (AI 검토 대기 중)", expanded=True):
                st.json(submission)
            st.info("담당자가 내용 확인 후 관련 수요자에게 매칭 리포트를 발송합니다.")

    return {}


# ─────────────────────────────────────────────────────────────────────────────
# 탭 2: 구합니다(수요자) 폼
# ─────────────────────────────────────────────────────────────────────────────
def render_demand_form():
    st.markdown("#### 🔍 수요 조건 상세 작성 (구합니다)")
    st.caption("원하시는 매물 조건을 상세히 입력해주세요.")
    st.divider()

    # ── 섹션 1: 기본 인적사항 ──────────────────────────────────────────────
    st.markdown("##### 👤 기본 인적사항 (필수)")
    c1, c2 = st.columns(2)
    d_name  = c1.text_input("이름", placeholder="홍길동", key="d_name")
    d_phone = c2.text_input("연락처", placeholder="010-1234-5678", key="d_phone")

    st.divider()

    # ── 섹션 2: 원하는 매물 종류 + 거래유형 ───────────────────────────────
    st.markdown("##### 🏷️ 희망 매물 종류 & 거래 유형")
    c1, c2 = st.columns(2)
    d_prop_type  = c1.selectbox("희망 매물 종류", PROPERTY_TYPES, key="d_prop_type")
    d_trade_type = c2.radio("희망 거래 유형", TRADE_TYPES, horizontal=True, key="d_trade_type")

    st.divider()

    # ── 섹션 3: 희망 단지/지역 ────────────────────────────────────────────
    st.markdown("##### 📍 희망 지역 & 단지")
    c1, c2 = st.columns(2)
    d_region  = c1.text_input("희망 지역 (구/동)", placeholder="예) 강남구 대치동, 송파구 잠실동", key="d_region")
    d_complex = c2.text_input("희망 단지명 (선택)", placeholder="예) 래미안 팰리스, 헬리오시티", key="d_complex")

    st.divider()

    # ── 섹션 4: 희망 면적 범위 ────────────────────────────────────────────
    st.markdown("##### 📐 희망 면적 범위")
    c1, c2 = st.columns(2)
    d_area_min = c1.number_input("최소 면적 (㎡)", min_value=0.0, step=1.0, format="%.1f", key="d_area_min")
    d_area_max = c2.number_input("최대 면적 (㎡)", min_value=0.0, step=1.0, format="%.1f", key="d_area_max")
    if d_area_min > 0 or d_area_max > 0:
        hint_parts = []
        if d_area_min > 0:
            hint_parts.append(f"최소 {sqm_to_pyeong(d_area_min)}평")
        if d_area_max > 0:
            hint_parts.append(f"최대 {sqm_to_pyeong(d_area_max)}평")
        st.info("≈ " + " ~ ".join(hint_parts))

    st.divider()

    # ── 섹션 5: 희망 가격 범위 ────────────────────────────────────────────
    st.markdown("##### 💵 희망 가격 범위")
    if d_trade_type == "매매":
        c1, c2 = st.columns(2)
        d_price_min = c1.number_input("매매가 최소 (억)", min_value=0.0, step=0.5, format="%.1f", key="d_price_min")
        d_price_max = c2.number_input("매매가 최대 (억)", min_value=0.0, step=0.5, format="%.1f", key="d_price_max")
        d_price_data = {"희망_매매가_최소_억": d_price_min, "희망_매매가_최대_억": d_price_max}
    elif d_trade_type == "전세":
        c1, c2 = st.columns(2)
        d_dep_min = c1.number_input("보증금 최소 (억)", min_value=0.0, step=0.5, format="%.1f", key="d_dep_min")
        d_dep_max = c2.number_input("보증금 최대 (억)", min_value=0.0, step=0.5, format="%.1f", key="d_dep_max")
        d_price_data = {"희망_보증금_최소_억": d_dep_min, "희망_보증금_최대_억": d_dep_max}
    else:  # 월세
        c1, c2, c3 = st.columns(3)
        d_dep_min   = c1.number_input("보증금 최소 (억)", min_value=0.0, step=0.1, format="%.1f", key="d_m_dep_min")
        d_dep_max   = c2.number_input("보증금 최대 (억)", min_value=0.0, step=0.1, format="%.1f", key="d_m_dep_max")
        d_rent_max  = c3.number_input("월세 최대 (만원)", min_value=0, step=5, key="d_rent_max")
        d_price_data = {
            "희망_보증금_최소_억": d_dep_min,
            "희망_보증금_최대_억": d_dep_max,
            "희망_월세_최대_만원": d_rent_max,
        }

    st.divider()

    # ── 섹션 6: 조건 체크박스 ────────────────────────────────────────────
    st.markdown("##### ✅ 희망 조건 선택 (해당 사항 모두 체크)")
    d_features = []
    feat_cols = st.columns(4)
    for i, feat in enumerate(FEATURES_DEMAND):
        if feat_cols[i % 4].checkbox(feat, key=f"d_feat_{i}"):
            d_features.append(feat)

    st.divider()

    # ── 섹션 7: 입주 희망일 + 기타 요청사항 ─────────────────────────────
    st.markdown("##### 📅 입주 희망일 & 기타 요청사항")
    c1, c2 = st.columns(2)
    d_move_date = c1.date_input(
        "입주 희망일",
        value=datetime.date.today() + datetime.timedelta(days=60),
        key="d_move_date"
    )
    d_memo = c2.text_area("기타 요청사항 (자유 기재)", placeholder="예) 반려동물 가능, 주차 2대 필수, 탑층 선호 등", height=100, key="d_memo")

    # ── 접수 버튼 ────────────────────────────────────────────────────────
    st.divider()
    if st.button("🔍 [구합니다] 수요 조건 접수하기", type="primary", use_container_width=True, key="btn_demand"):
        errors = []
        if not d_name:   errors.append("이름을 입력해주세요.")
        if not d_phone:  errors.append("연락처를 입력해주세요.")
        if not d_region: errors.append("희망 지역을 입력해주세요.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            submission = {
                "접수유형": "구합니다(수요)",
                "이름": d_name,
                "연락처": d_phone,
                "희망_매물종류": d_prop_type,
                "희망_거래유형": d_trade_type,
                "희망_지역": d_region,
                "희망_단지": d_complex,
                "희망_면적_㎡": f"{d_area_min} ~ {d_area_max}",
                "희망_면적_평": f"{sqm_to_pyeong(d_area_min)} ~ {sqm_to_pyeong(d_area_max)}",
                **d_price_data,
                "희망_조건": d_features,
                "입주희망일": str(d_move_date),
                "기타요청": d_memo,
                "접수시각": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            with st.spinner("🔒 보안 서버에 암호화하여 전송 중입니다..."):
                time.sleep(1.2)

            st.success("✅ [구합니다] 수요 조건 접수가 완료되었습니다!")
            st.balloons()
            with st.expander("📊 접수 내용 확인 (AI 매칭 대기 중)", expanded=True):
                st.json(submission)
            st.info("AI가 조건에 맞는 매물을 분석하여 담당자가 연락드립니다.")

    return {}


# ─────────────────────────────────────────────────────────────────────────────
# 메인 진입점 (main 함수로 래핑 - 03_ai_matching.py에서 importlib로 호출)
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.title("🤖 AI 사전 매칭 예약")
    st.markdown(
        "**파발마 한방 스타일**의 상세 물건 접수 폼입니다.  \n"
        "**있습니다(공급)** 탭은 내 물건을 내놓을 때, **구합니다(수요)** 탭은 원하는 매물을 찾을 때 사용하세요."
    )

    tab_supply, tab_demand = st.tabs(["🏠 있습니다 (공급/매도·임대)", "🔍 구합니다 (수요/매수·임차)"])

    with tab_supply:
        render_supply_form()

    with tab_demand:
        render_demand_form()


# ─────────────────────────────────────────────────────────────────────────────
# 직접 실행 시 (streamlit run pages/ai_matching_reservation.py)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    st.set_page_config(
        page_title="AI 사전 매칭 예약",
        page_icon="🤖",
        layout="wide"
    )
    main()
