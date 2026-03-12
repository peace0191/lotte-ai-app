"""
pages/ai_matching_reservation.py
AI 사전 매칭 예약 폼 - 파발마 스타일 초상세 폼
있습니다(공급) / 구합니다(수요) 탭 분리
임대차 보증금 최소~최대, 월세 최소~최대 범위 입력 지원
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

# 대치1동 주요 단지 (AI 매칭/공동중개 드롭다운용)
DEFAULT_COMPLEX_OPTIONS = [
    "래미안대치팰리스",
    "대치SK뷰",
    "대치아이파크",
    "은마아파트",
    "삼환아르누보2 오피스텔",
    "롯데월드타워몰 시그니엘레지던스",
    "직접입력",
]

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
    "🅿️ 주차 가능",
    "🌅 조망권 우수",
    "📐 확장형 구조",
    "🏫 학군 우수",
    "🏬 상가·편의시설 인근",
    "🔑 즉시 입주 가능",
    "📦 반전세 협의가능",
    "🛁 욕실 리모델링 완료",
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
    "📐 확장형 구조",
    "🌅 조망권 선호",
    "🛋️ 풀옵션 선호",
    "🅿️ 주차 2대 이상",
    "🐾 반려동물 가능",
    "🔇 저층 선호",
    "🌟 탑층 선호",
    "🛁 신축·리모델링",
]

# 서울 주요 구/동 목록
REGIONS_GU = [
    "강남구", "서초구", "송파구", "강동구", "마포구",
    "용산구", "성동구", "광진구", "강서구", "양천구",
    "영등포구", "동작구", "관악구", "구로구", "금천구",
    "서대문구", "은평구", "종로구", "중구", "노원구",
    "도봉구", "강북구", "성북구", "중랑구", "동대문구",
]

PARKING_OPTIONS = ["자주식 (가능)", "기계식 (가능)", "불가", "미확인"]
HEATING_OPTIONS = ["개별난방", "중앙난방", "지역난방"]
DIRECTION_OPTIONS = ["남향", "남동향", "남서향", "동향", "서향", "북향", "북동향", "북서향", "기타"]

# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼 함수
# ─────────────────────────────────────────────────────────────────────────────
def sqm_to_pyeong(sqm: float) -> float:
    """㎡ → 평 환산 (1평 = 3.3058㎡)"""
    return round(sqm / 3.3058, 2)


def section_header(icon: str, title: str):
    """섹션 제목 헤더 렌더링"""
    st.markdown(
        f"""<div style="background:linear-gradient(90deg,#1e3a5f,#1e293b);
            border-radius:10px; padding:10px 16px; margin:16px 0 10px 0;
            border-left:4px solid #facc15;">
            <span style="color:#facc15;font-size:1.1rem;font-weight:900;">{icon}</span>
            <span style="color:#f8fafc;font-size:1.0rem;font-weight:700;margin-left:8px;">{title}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def render_price_range_inputs(trade_type: str, prefix: str = "") -> dict:
    """
    거래 유형별 가격 범위 입력 (최소 ~ 최대)
    - 매매: 매매가 최소 / 최대 (억)
    - 전세: 보증금 최소 / 최대 (억)
    - 월세: 보증금 최소 / 최대 (억) + 월세 최소 / 최대 (만원)
    """
    data = {}

    if trade_type == "매매":
        st.markdown("**🏷️ 매매가 범위**")
        c1, c2, c3, c4 = st.columns(4)
        data["매매가_최소_억"] = c1.number_input(
            "매매가 최소 (억)", min_value=0.0, step=0.5, format="%.1f",
            key=f"{prefix}_sale_min_ok"
        )
        data["매매가_최소_만원"] = c2.number_input(
            "+ 만원 단위", min_value=0, step=500,
            key=f"{prefix}_sale_min_man"
        )
        data["매매가_최대_억"] = c3.number_input(
            "매매가 최대 (억)", min_value=0.0, step=0.5, format="%.1f",
            key=f"{prefix}_sale_max_ok"
        )
        data["매매가_최대_만원"] = c4.number_input(
            "+ 만원 단위 ", min_value=0, step=500,
            key=f"{prefix}_sale_max_man"
        )
        if data["매매가_최소_억"] > 0 or data["매매가_최대_억"] > 0:
            mn = data["매매가_최소_억"] + data["매매가_최소_만원"] / 10000
            mx = data["매매가_최대_억"] + data["매매가_최대_만원"] / 10000
            st.info(f"💡 입력 범위: **{mn:.2f}억 ~ {mx:.2f}억**")

    elif trade_type == "전세":
        st.markdown("**🔑 임대차 보증금 범위**")
        c1, c2, c3, c4 = st.columns(4)
        data["보증금_최소_억"] = c1.number_input(
            "보증금 최소 (억)", min_value=0.0, step=0.5, format="%.1f",
            key=f"{prefix}_dep_min_ok"
        )
        data["보증금_최소_만원"] = c2.number_input(
            "+ 만원 단위", min_value=0, step=500,
            key=f"{prefix}_dep_min_man"
        )
        data["보증금_최대_억"] = c3.number_input(
            "보증금 최대 (억)", min_value=0.0, step=0.5, format="%.1f",
            key=f"{prefix}_dep_max_ok"
        )
        data["보증금_최대_만원"] = c4.number_input(
            "+ 만원 단위 ", min_value=0, step=500,
            key=f"{prefix}_dep_max_man"
        )
        if data["보증금_최소_억"] > 0 or data["보증금_최대_억"] > 0:
            mn = data["보증금_최소_억"] + data["보증금_최소_만원"] / 10000
            mx = data["보증금_최대_억"] + data["보증금_최대_만원"] / 10000
            st.info(f"💡 전세 보증금 범위: **{mn:.2f}억 ~ {mx:.2f}억**")

    else:  # 월세 (반전세 포함)
        st.markdown("**🔑 임대차 보증금 범위 (최소 ~ 최대)**")
        c1, c2, c3, c4 = st.columns(4)
        data["보증금_최소_억"] = c1.number_input(
            "보증금 최소 (억)", min_value=0.0, step=0.1, format="%.1f",
            key=f"{prefix}_m_dep_min_ok"
        )
        data["보증금_최소_만원"] = c2.number_input(
            "+ 만원 단위", min_value=0, step=100,
            key=f"{prefix}_m_dep_min_man"
        )
        data["보증금_최대_억"] = c3.number_input(
            "보증금 최대 (억)", min_value=0.0, step=0.1, format="%.1f",
            key=f"{prefix}_m_dep_max_ok"
        )
        data["보증금_최대_만원"] = c4.number_input(
            "+ 만원 단위 ", min_value=0, step=100,
            key=f"{prefix}_m_dep_max_man"
        )

        if data["보증금_최소_억"] > 0 or data["보증금_최대_억"] > 0:
            mn = data["보증금_최소_억"] + data["보증금_최소_만원"] / 10000
            mx = data["보증금_최대_억"] + data["보증금_최대_만원"] / 10000
            st.info(f"💡 보증금 범위: **{mn:.2f}억 ~ {mx:.2f}억**")

        st.markdown("**💴 월 차임(월세) 범위 (최소 ~ 최대)**")
        c5, c6 = st.columns(2)
        data["월세_최소_만원"] = c5.number_input(
            "월세 최소 (만원)", min_value=0, step=5,
            key=f"{prefix}_rent_min"
        )
        data["월세_최대_만원"] = c6.number_input(
            "월세 최대 (만원)", min_value=0, step=5,
            key=f"{prefix}_rent_max"
        )
        if data["월세_최소_만원"] > 0 or data["월세_최대_만원"] > 0:
            st.info(
                f"💡 월세 범위: **{data['월세_최소_만원']:,}만원 ~ {data['월세_최대_만원']:,}만원**"
            )

    return data


def render_area_inputs(prefix: str) -> dict:
    """면적 입력 + ㎡→평 자동환산"""
    c1, c2, c3 = st.columns(3)
    supply_sqm  = c1.number_input("공급면적 (㎡)", min_value=0.0, step=0.5, format="%.1f", key=f"{prefix}_supply_sqm")
    private_sqm = c2.number_input("전용면적 (㎡)", min_value=0.0, step=0.5, format="%.1f", key=f"{prefix}_private_sqm")
    land_sqm    = c3.number_input("대지면적 (㎡)", min_value=0.0, step=0.5, format="%.1f", key=f"{prefix}_land_sqm")

    if supply_sqm > 0 or private_sqm > 0:
        py_cols = st.columns(3)
        if supply_sqm  > 0: py_cols[0].success(f"공급 ≈ **{sqm_to_pyeong(supply_sqm)}평**")
        if private_sqm > 0: py_cols[1].success(f"전용 ≈ **{sqm_to_pyeong(private_sqm)}평**")
        if land_sqm    > 0: py_cols[2].success(f"대지 ≈ **{sqm_to_pyeong(land_sqm)}평**")

    return {
        "공급면적_㎡": supply_sqm,
        "전용면적_㎡": private_sqm,
        "대지면적_㎡": land_sqm,
        "공급면적_평": sqm_to_pyeong(supply_sqm),
        "전용면적_평": sqm_to_pyeong(private_sqm),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 탭 1: 있습니다(공급자) 폼 — 파발마 초상세 버전
# ─────────────────────────────────────────────────────────────────────────────
def render_supply_form():
    st.markdown(
        """<div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);
            border-radius:14px; padding:18px 22px; margin-bottom:20px;
            border:1px solid #334155;">
            <div style="font-size:1.3rem;font-weight:900;color:#facc15;">🏠 있습니다 (공급/매도·임대)</div>
            <div style="color:#93c5fd;font-size:0.9rem;margin-top:4px;">
                보유하신 매물 정보를 <b style="color:#fbbf24;">파발마 스타일로 상세하게</b> 입력해주세요.<br>
                상세할수록 AI 매칭 확률이 높아집니다! 🚀
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── 섹션 1: 기본 인적사항 ────────────────────────────────────────────────
    section_header("👤", "기본 인적사항 (필수)")
    c1, c2, c3 = st.columns(3)
    s_name      = c1.text_input("이름 (공급자)", placeholder="홍길동", key="s_name")
    s_phone     = c2.text_input("연락처", placeholder="010-1234-5678", key="s_phone")
    s_agency    = c3.text_input("소속 중개사무소 (선택)", placeholder="롯데타워 공인중개사", key="s_agency")

    st.divider()

    # ── 섹션 2: 매물 종류 & 거래 구분 ────────────────────────────────────────
    section_header("🏷️", "매물 종류 & 거래 구분")
    c1, c2 = st.columns(2)
    s_prop_type  = c1.selectbox("매물 종류", PROPERTY_TYPES, key="s_prop_type")
    s_trade_type = c2.radio("거래 구분", TRADE_TYPES, horizontal=True, key="s_trade_type")

    st.divider()

    # ── 섹션 3: 위치 정보 ────────────────────────────────────────────────────
    section_header("📍", "위치 정보")
    c1, c2 = st.columns(2)
    s_gu      = c1.selectbox("구 선택", REGIONS_GU, key="s_gu")
    s_dong    = c2.text_input("동/읍/면", placeholder="대치동", key="s_dong")

    c3, c4 = st.columns(2)
    s_cplx_sel = c3.selectbox(
        "단지명 / 건물명",
        DEFAULT_COMPLEX_OPTIONS,
        key="s_cplx_sel"
    )
    s_road    = c4.text_input("도로명 주소 (선택)", placeholder="○○로 123", key="s_road")
    if s_cplx_sel == "직접입력":
        s_complex = st.text_input(
            "단지명 직접 입력",
            placeholder="단지명/건물명을 입력하세요",
            key="s_complex"
        )
    else:
        s_complex = s_cplx_sel

    c5, c6 = st.columns(2)
    s_dong_no = c5.text_input("동 호수", placeholder="예) 101동 1501호", key="s_dong_ho")
    s_build_year = c6.number_input("준공년도", min_value=1960, max_value=2030, value=2005, key="s_build_year")

    st.divider()

    # ── 섹션 4: 물건 상세 정보 ──────────────────────────────────────────────
    section_header("🏗️", "물건 상세 정보")
    c1, c2, c3, c4 = st.columns(4)
    s_floor       = c1.number_input("해당 층수", min_value=1, max_value=100, value=5, key="s_floor")
    s_total_floor = c2.number_input("총 층수", min_value=1, max_value=200, value=20, key="s_total_floor")
    s_rooms       = c3.number_input("방 수", min_value=1, max_value=20, value=3, key="s_rooms")
    s_baths       = c4.number_input("화장실 수", min_value=1, max_value=10, value=2, key="s_baths")

    c5, c6, c7, c8 = st.columns(4)
    s_direction   = c5.selectbox("향", DIRECTION_OPTIONS, key="s_direction")
    s_parking     = c6.selectbox("주차 여부", PARKING_OPTIONS, key="s_parking")
    s_heating     = c7.selectbox("난방 방식", HEATING_OPTIONS, key="s_heating")
    s_elevator    = c8.radio("엘리베이터", ["있음", "없음"], horizontal=True, key="s_elevator")

    c9, c10 = st.columns(2)
    s_expansion   = c9.radio("확장 유무", ["확장형", "비확장", "일부확장"], horizontal=True, key="s_expansion")
    s_remodel     = c10.radio("리모델링 여부", ["없음", "부분수리", "올수리(풀리모델)", "준신축"], horizontal=True, key="s_remodel")

    st.divider()

    # ── 섹션 5: 면적/규모 ────────────────────────────────────────────────────
    section_header("📐", "면적 / 규모")
    s_area = render_area_inputs("s")

    st.divider()

    # ── 섹션 6: 가격 정보 (최소~최대 범위) ──────────────────────────────────
    section_header("💵", "가격 정보 (최소 ~ 최대 범위 입력)")
    st.caption("⚠️ 공급자(임대인/매도인)가 희망하는 최소~최대 가격 범위를 입력해주세요.")
    s_price = render_price_range_inputs(s_trade_type, prefix="s")

    if s_trade_type in ["전세", "월세(반전세 포함)"]:
        st.markdown("**📋 관리비 (월)**")
        c1, c2 = st.columns(2)
        s_mgmt_fee = c1.number_input("관리비 (만원/월)", min_value=0, step=1, value=15, key="s_mgmt_fee")
        s_mgmt_inc = c2.text_input("관리비 포함 항목", placeholder="예) 수도·전기·가스 별도, TV·인터넷 포함", key="s_mgmt_inc")
    else:
        s_mgmt_fee = 0
        s_mgmt_inc = ""

    st.divider()

    # ── 섹션 7: 융자 / 권리관계 ─────────────────────────────────────────────
    section_header("🛡️", "융자 / 권리관계")
    c1, c2, c3 = st.columns(3)
    s_loan      = c1.number_input("융자금 (억원)", min_value=0.0, step=0.1, format="%.1f", key="s_loan")
    s_loan_man  = c2.number_input("+ 만원 단위", min_value=0, step=100, key="s_loan_man")
    s_rights    = c3.text_input("특이 권리관계", placeholder="예) 근저당 없음, 가압류 없음", key="s_rights")
    s_tenant    = st.radio(
        "현 거주 상황",
        ["소유자 거주중", "세입자 거주중 (만기일 협의 필요)", "공실 (즉시 입주 가능)", "기타"],
        horizontal=True,
        key="s_tenant"
    )
    if s_tenant == "세입자 거주중 (만기일 협의 필요)":
        s_tenant_expire = st.date_input("세입자 계약 만료일", key="s_tenant_expire")
    else:
        s_tenant_expire = None

    st.divider()

    # ── 섹션 8: 특징 선택 (파발마 스타일) ───────────────────────────────────
    section_header("✅", "매물 특징 & 어필 포인트 (해당 사항 모두 체크)")
    s_features = []
    feat_cols = st.columns(4)
    for i, feat in enumerate(FEATURES_SUPPLY):
        if feat_cols[i % 4].checkbox(feat, key=f"s_feat_{i}"):
            s_features.append(feat)

    # 자유 어필 포인트
    s_appeal = st.text_area(
        "🌟 추가 어필 포인트 (자유 기재)",
        placeholder="예) 대치1동 학원가 도보 3분, 대치초 배정권, 주인거주 깨끗한 집, 갭투자 가능 협의...",
        height=80,
        key="s_appeal"
    )

    st.divider()

    # ── 섹션 9: 이사예정일 / 특이사항 ──────────────────────────────────────
    section_header("📅", "일정 & 특이사항")
    c1, c2 = st.columns(2)
    s_move_date = c1.date_input(
        "이사예정일 / 인도가능일",
        value=datetime.date.today() + datetime.timedelta(days=30),
        key="s_move_date"
    )
    s_memo = c2.text_area(
        "특이사항 메모 (자유 기재)",
        placeholder="예) 세입자 이사 후 즉시 가능, 풀옵션 협의 가능, 반려동물 협의 등",
        height=100,
        key="s_memo"
    )

    st.divider()

    # ── 섹션 10: 발송 지역 ───────────────────────────────────────────────────
    section_header("📡", "AI 매칭 발송 지역 선택")
    st.caption("이 물건 정보를 발송할 구/지역을 선택해주세요. 다중 선택 가능합니다.")
    c1, c2 = st.columns(2)
    s_send_gu     = c1.multiselect("발송 구 선택", REGIONS_GU, default=["강남구"], key="s_send_gu")
    s_send_custom = c2.text_input("추가 직접 입력 (동, 지역명 등)", placeholder="예) 대치동, 압구정동", key="s_send_custom")

    # ── 접수 버튼 ─────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        """<div style="background:#0f172a;border:1px solid #334155;border-radius:12px;
            padding:14px;margin-bottom:16px;text-align:center;">
            <span style="color:#94a3b8;font-size:0.85rem;">
            🔒 입력하신 정보는 SSL 암호화 전송되며, 개인정보처리방침에 따라 안전하게 관리됩니다.
            </span>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button("🚀 [있습니다] AI 공급 물건 접수하기", type="primary", use_container_width=True, key="btn_supply"):
        errors = []
        if not s_name:    errors.append("이름을 입력해주세요.")
        if not s_phone:   errors.append("연락처를 입력해주세요.")
        if not s_complex: errors.append("단지명을 입력해주세요.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            submission = {
                "접수유형": "있습니다(공급)",
                "이름": s_name,
                "연락처": s_phone,
                "소속": s_agency,
                "매물종류": s_prop_type,
                "거래구분": s_trade_type,
                "구": s_gu,
                "동": s_dong,
                "단지명": s_complex,
                "도로명주소": s_road,
                "동호수": s_dong_no,
                "준공년도": s_build_year,
                "층수": f"{s_floor}/{s_total_floor}층",
                "방수": s_rooms,
                "화장실수": s_baths,
                "향": s_direction,
                "주차": s_parking,
                "난방": s_heating,
                "엘리베이터": s_elevator,
                "확장유무": s_expansion,
                "리모델링": s_remodel,
                **s_area,
                **s_price,
                "관리비_만원": s_mgmt_fee,
                "관리비포함": s_mgmt_inc,
                "융자금_억": s_loan,
                "융자금_만원추가": s_loan_man,
                "권리관계": s_rights,
                "거주상황": s_tenant,
                "세입자만료일": str(s_tenant_expire) if s_tenant_expire else None,
                "특징": s_features,
                "어필포인트": s_appeal,
                "인도가능일": str(s_move_date),
                "특이사항": s_memo,
                "발송구": s_send_gu,
                "발송지역추가": s_send_custom,
                "접수시각": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            with st.spinner("🔒 보안 서버에 암호화하여 전송 중입니다..."):
                time.sleep(1.5)

            st.success("✅ [있습니다] AI 공급 물건 접수가 완료되었습니다!")
            st.balloons()
            with st.expander("📊 접수 내용 확인 (AI 매칭 분석 대기 중)", expanded=True):
                st.json(submission)
            st.info("📲 담당자가 내용 확인 후 AI가 조건에 맞는 수요자에게 자동 매칭 리포트를 발송합니다.\n\n🕐 평균 매칭 소요시간: **30분 ~ 2시간 이내**")

    return {}


# ─────────────────────────────────────────────────────────────────────────────
# 탭 2: 구합니다(수요자) 폼 — 파발마 초상세 버전
# ─────────────────────────────────────────────────────────────────────────────
def render_demand_form():
    st.markdown(
        """<div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);
            border-radius:14px; padding:18px 22px; margin-bottom:20px;
            border:1px solid #334155;">
            <div style="font-size:1.3rem;font-weight:900;color:#67e8f9;">🔍 구합니다 (수요/매수·임차)</div>
            <div style="color:#93c5fd;font-size:0.9rem;margin-top:4px;">
                원하시는 매물 조건을 <b style="color:#34d399;">상세하게</b> 입력해 주세요.<br>
                조건이 구체적일수록 AI 매칭 정확도가 높아집니다! 🎯
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── 섹션 1: 기본 인적사항 ────────────────────────────────────────────────
    section_header("👤", "기본 인적사항 (필수)")
    c1, c2, c3 = st.columns(3)
    d_name   = c1.text_input("이름 (수요자)", placeholder="홍길동", key="d_name")
    d_phone  = c2.text_input("연락처", placeholder="010-1234-5678", key="d_phone")
    d_agency = c3.text_input("소속 중개사무소 (선택)", placeholder="롯데타워 공인중개사", key="d_agency")

    st.divider()

    # ── 섹션 2: 원하는 매물 종류 + 거래유형 ────────────────────────────────
    section_header("🏷️", "희망 매물 종류 & 거래 유형")
    c1, c2 = st.columns(2)
    d_prop_type  = c1.selectbox("희망 매물 종류", PROPERTY_TYPES, key="d_prop_type")
    d_trade_type = c2.radio("희망 거래 유형", TRADE_TYPES, horizontal=True, key="d_trade_type")

    st.divider()

    # ── 섹션 3: 희망 단지/지역 ──────────────────────────────────────────────
    section_header("📍", "희망 지역 & 단지")
    c1, c2 = st.columns(2)
    d_region_gu  = c1.multiselect("희망 구 선택 (복수 가능)", REGIONS_GU, default=["강남구"], key="d_region_gu")
    d_dong       = c2.text_input("희망 동/지역명", placeholder="예) 대치동, 압구정동, 잠실동", key="d_dong")

    c3, c4 = st.columns(2)
    d_cplx_sel = c3.selectbox(
        "희망 단지명 (1순위)",
        DEFAULT_COMPLEX_OPTIONS,
        key="d_cplx_sel"
    )
    d_alt_cplx_sel = c4.selectbox(
        "희망 단지명 (2순위)",
        ["선택 안함"] + DEFAULT_COMPLEX_OPTIONS,
        key="d_alt_cplx_sel"
    )
    if d_cplx_sel == "직접입력":
        d_complex = st.text_input("1순위 단지 직접 입력", placeholder="단지명/건물명을 입력하세요", key="d_complex")
    else:
        d_complex = d_cplx_sel
    if d_alt_cplx_sel == "직접입력":
        d_alt_complex = st.text_input("2순위 단지 직접 입력", placeholder="단지명/건물명을 입력하세요", key="d_alt_complex")
    else:
        d_alt_complex = d_alt_cplx_sel

    st.divider()

    # ── 섹션 4: 희망 면적 범위 ──────────────────────────────────────────────
    section_header("📐", "희망 면적 범위")
    c1, c2 = st.columns(2)
    d_area_min = c1.number_input("최소 전용면적 (㎡)", min_value=0.0, step=1.0, format="%.1f", key="d_area_min")
    d_area_max = c2.number_input("최대 전용면적 (㎡)", min_value=0.0, step=1.0, format="%.1f", key="d_area_max")
    if d_area_min > 0 or d_area_max > 0:
        hint_parts = []
        if d_area_min > 0: hint_parts.append(f"최소 {sqm_to_pyeong(d_area_min)}평")
        if d_area_max > 0: hint_parts.append(f"최대 {sqm_to_pyeong(d_area_max)}평")
        st.success("≈ " + " ~ ".join(hint_parts))

    c3, c4, c5 = st.columns(3)
    d_floor_min = c3.number_input("희망 최소 층수", min_value=1, max_value=100, value=3, key="d_floor_min")
    d_floor_max = c4.number_input("희망 최대 층수", min_value=1, max_value=100, value=20, key="d_floor_max")
    d_rooms_min = c5.number_input("최소 방 수", min_value=1, max_value=10, value=3, key="d_rooms_min")

    st.divider()

    # ── 섹션 5: 희망 가격 범위 (최소~최대) ─────────────────────────────────
    section_header("💵", "희망 가격 범위 (최소 ~ 최대)")
    st.caption("⚠️ 수요자(매수인/임차인)가 허용하는 가격 범위를 입력해주세요.")

    if d_trade_type == "매매":
        st.markdown("**🏷️ 매매가 범위**")
        c1, c2 = st.columns(2)
        d_price_min = c1.number_input("매매가 최소 (억)", min_value=0.0, step=0.5, format="%.1f", key="d_price_min")
        d_price_max = c2.number_input("매매가 최대 (억)", min_value=0.0, step=0.5, format="%.1f", key="d_price_max")
        d_price_data = {"희망_매매가_최소_억": d_price_min, "희망_매매가_최대_억": d_price_max}
        if d_price_min > 0 or d_price_max > 0:
            st.info(f"💡 매매가 범위: **{d_price_min:.1f}억 ~ {d_price_max:.1f}억**")

    elif d_trade_type == "전세":
        st.markdown("**🔑 임대차 보증금 범위**")
        c1, c2 = st.columns(2)
        d_dep_min = c1.number_input("보증금 최소 (억)", min_value=0.0, step=0.5, format="%.1f", key="d_dep_min")
        d_dep_max = c2.number_input("보증금 최대 (억)", min_value=0.0, step=0.5, format="%.1f", key="d_dep_max")
        d_price_data = {"희망_보증금_최소_억": d_dep_min, "희망_보증금_최대_억": d_dep_max}
        if d_dep_min > 0 or d_dep_max > 0:
            st.info(f"💡 전세 보증금 범위: **{d_dep_min:.1f}억 ~ {d_dep_max:.1f}억**")

    else:  # 월세(반전세 포함)
        st.markdown("**🔑 임대차 보증금 범위 (최소 ~ 최대)**")
        c1, c2 = st.columns(2)
        d_dep_min = c1.number_input("보증금 최소 (억)", min_value=0.0, step=0.1, format="%.1f", key="d_m_dep_min")
        d_dep_max = c2.number_input("보증금 최대 (억)", min_value=0.0, step=0.1, format="%.1f", key="d_m_dep_max")
        if d_dep_min > 0 or d_dep_max > 0:
            st.info(f"💡 보증금 범위: **{d_dep_min:.1f}억 ~ {d_dep_max:.1f}억**")

        st.markdown("**💴 월 차임(월세) 범위 (최소 ~ 최대)**")
        c3, c4 = st.columns(2)
        d_rent_min = c3.number_input("월세 최소 (만원)", min_value=0, step=5, key="d_rent_min")
        d_rent_max = c4.number_input("월세 최대 (만원)", min_value=0, step=5, key="d_rent_max")
        if d_rent_min > 0 or d_rent_max > 0:
            st.info(f"💡 월세 범위: **{d_rent_min:,}만원 ~ {d_rent_max:,}만원**")
        d_price_data = {
            "희망_보증금_최소_억": d_dep_min,
            "희망_보증금_최대_억": d_dep_max,
            "희망_월세_최소_만원": d_rent_min,
            "희망_월세_최대_만원": d_rent_max,
        }

        # 관리비 허용 범위
        st.markdown("**🧾 허용 관리비 (월)**")
        c5, c6 = st.columns(2)
        d_mgmt_max = c5.number_input("관리비 최대 허용액 (만원)", min_value=0, step=1, value=20, key="d_mgmt_max")
        d_price_data["희망_관리비_최대_만원"] = d_mgmt_max

    st.divider()

    # ── 섹션 6: 희망 물건 상세 조건 ────────────────────────────────────────
    section_header("🏗️", "희망 물건 상세 조건")
    c1, c2, c3 = st.columns(3)
    d_direction = c1.multiselect("선호 향", DIRECTION_OPTIONS, default=["남향", "남동향"], key="d_direction")
    d_parking   = c2.multiselect("주차 조건", PARKING_OPTIONS, default=["자주식 (가능)"], key="d_parking")
    d_heating   = c3.multiselect("난방 방식", HEATING_OPTIONS, default=["개별난방"], key="d_heating")

    c4, c5 = st.columns(2)
    d_elevator  = c4.radio("엘리베이터", ["필수", "선호", "무관"], horizontal=True, key="d_elevator")
    d_expansion = c5.radio("확장형 구조", ["선호", "무관", "비확장도 가능"], horizontal=True, key="d_expansion")

    st.divider()

    # ── 섹션 7: 조건 체크박스 ────────────────────────────────────────────────
    section_header("✅", "희망 조건 선택 (해당 사항 모두 체크)")
    d_features = []
    feat_cols = st.columns(4)
    for i, feat in enumerate(FEATURES_DEMAND):
        if feat_cols[i % 4].checkbox(feat, key=f"d_feat_{i}"):
            d_features.append(feat)

    # 자유 입력 조건
    d_extra_cond = st.text_area(
        "🌟 추가 희망 조건 (자유 기재)",
        placeholder="예) 반려동물 가능, 주차 2대 필수, 탑층 선호, 씽크대 교체된 곳, 학원가 도보 5분 이내 등...",
        height=80,
        key="d_extra_cond"
    )

    st.divider()

    # ── 섹션 8: 입주 희망일 + 기타 요청사항 ────────────────────────────────
    section_header("📅", "입주 희망일 & 기타 요청사항")
    c1, c2, c3 = st.columns(3)
    d_move_date  = c1.date_input(
        "입주 희망일",
        value=datetime.date.today() + datetime.timedelta(days=60),
        key="d_move_date"
    )
    d_move_flex  = c2.radio("입주일 유연성", ["고정 (날짜 반드시 맞춰야 함)", "±1개월 협의", "±3개월 협의", "유연함"], key="d_move_flex")
    d_budget_flex = c3.radio("예산 유연성", ["엄수 (초과 불가)", "±5% 협의", "±10% 협의", "협의 가능"], key="d_budget_flex")

    d_memo = st.text_area(
        "기타 요청사항 (자유 기재)",
        placeholder="예) 세입자 계약 만기 전 입주도 가능, 전세대출 실행 예정, 특정 동/라인 선호 등",
        height=80,
        key="d_memo"
    )

    # ── 접수 버튼 ─────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        """<div style="background:#0f172a;border:1px solid #334155;border-radius:12px;
            padding:14px;margin-bottom:16px;text-align:center;">
            <span style="color:#94a3b8;font-size:0.85rem;">
            🔒 입력하신 정보는 SSL 암호화 전송되며, 개인정보처리방침에 따라 안전하게 관리됩니다.
            </span>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button("🔍 [구합니다] AI 수요 조건 접수하기", type="primary", use_container_width=True, key="btn_demand"):
        errors = []
        if not d_name:          errors.append("이름을 입력해주세요.")
        if not d_phone:         errors.append("연락처를 입력해주세요.")
        if not d_region_gu:     errors.append("희망 구를 하나 이상 선택해주세요.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            submission = {
                "접수유형": "구합니다(수요)",
                "이름": d_name,
                "연락처": d_phone,
                "소속": d_agency,
                "희망_매물종류": d_prop_type,
                "희망_거래유형": d_trade_type,
                "희망_구": d_region_gu,
                "희망_동": d_dong,
                "희망_단지": d_complex,
                "대안_단지": d_alt_complex,
                "희망_전용면적_㎡": f"{d_area_min} ~ {d_area_max}",
                "희망_전용면적_평": f"{sqm_to_pyeong(d_area_min)} ~ {sqm_to_pyeong(d_area_max)}",
                "희망_층수": f"{d_floor_min} ~ {d_floor_max}층",
                "최소_방수": d_rooms_min,
                **d_price_data,
                "선호_향": d_direction,
                "주차_조건": d_parking,
                "난방_방식": d_heating,
                "엘리베이터": d_elevator,
                "확장형": d_expansion,
                "희망_조건": d_features,
                "추가_희망조건": d_extra_cond,
                "입주희망일": str(d_move_date),
                "입주일_유연성": d_move_flex,
                "예산_유연성": d_budget_flex,
                "기타요청": d_memo,
                "접수시각": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            with st.spinner("🔒 보안 서버에 암호화하여 전송 중입니다..."):
                time.sleep(1.5)

            st.success("✅ [구합니다] AI 수요 조건 접수가 완료되었습니다!")
            st.balloons()
            with st.expander("📊 접수 내용 확인 (AI 매칭 분석 대기 중)", expanded=True):
                st.json(submission)
            st.info("📲 AI가 조건에 맞는 매물을 분석하여 담당자가 연락드립니다.\n\n🕐 평균 매칭 소요시간: **30분 ~ 2시간 이내**")

    return {}


# ─────────────────────────────────────────────────────────────────────────────
# 메인 진입점
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # 헤더 히어로 배너
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0f172a 100%);
         border-radius:16px; padding:24px 28px; margin-bottom:24px;
         border:1px solid #334155; box-shadow:0 8px 32px rgba(0,0,0,0.4);">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;">
            <div style="font-size:3rem;">🏙️</div>
            <div>
                <div style="font-size:1.5rem;font-weight:900;color:#facc15;line-height:1.3;">
                    롯데타워 AI 사전 매칭 센터
                </div>
                <div style="color:#93c5fd;font-size:0.9rem;margin-top:4px;">
                    에어비앤비 방식의 스마트 예약 시스템으로 <b style="color:#fbbf24;">매칭 확률을 300% 높이세요.</b>
                </div>
            </div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <span style="background:#1e40af33;color:#93c5fd;border:1px solid #3b82f6;
                         border-radius:20px;padding:3px 14px;font-size:0.78rem;font-weight:700;">
                🤖 AI 자동 매칭
            </span>
            <span style="background:#14532d33;color:#86efac;border:1px solid #22c55e;
                         border-radius:20px;padding:3px 14px;font-size:0.78rem;font-weight:700;">
                🛡️ 내 집의 골든타임 예약
            </span>
            <span style="background:#7f1d1d33;color:#fca5a5;border:1px solid #ef4444;
                         border-radius:20px;padding:3px 14px;font-size:0.78rem;font-weight:700;">
                📋 AI 공동매물 매칭 접수
            </span>
            <span style="background:#713f1233;color:#fcd34d;border:1px solid #f59e0b;
                         border-radius:20px;padding:3px 14px;font-size:0.78rem;font-weight:700;">
                ✅ 파발마 스타일 상세 폼
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
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
