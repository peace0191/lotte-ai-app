"""
pages/naver_ai_home.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 네이버 Pay AI 집찾기 × 롯데타워 AI 앱 연동 센터
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
네이버 AI 집찾기의 자연어 검색 기능을 우리 앱 수요자 폼과 연결:
1. 수요 조건 입력 → 자연어 쿼리 자동 생성
2. 네이버 부동산 URL 딥링크 연결
3. Npay 앱 QR코드 표시
"""

import streamlit as st
import urllib.parse

# ─────────────────────────────────────────────
NAVER_LAND_BASE   = "https://land.naver.com/"
NAVER_AI_CAMPAIGN = "https://campaign2.naver.com/npay/land_ai/#"
NPAY_QRCODE_URL   = "https://campaign2.naver.com/npay/land_ai/#"   # QR 대상 URL

PROP_TYPES_MAP = {
    "아파트": "아파트",
    "오피스텔": "오피스텔",
    "빌라/연립": "빌라",
    "상가": "상가",
    "토지": "토지",
    "기타": "부동산",
}
DEAL_MAP = {
    "매수 (사기)": "매매",
    "전세 찾기": "전세",
    "월세 찾기": "월세",
    "반전세": "반전세",
}

# ─────────────────────────────────────────────
def build_naver_query(region: str, prop_type: str, deal_type: str,
                      area_min: float, area_max: float,
                      dep_min: int, dep_max: int,
                      monthly_min: int, monthly_max: int,
                      conditions: list) -> str:
    """수요 조건 → 네이버 AI 자연어 쿼리 자동 생성"""
    parts = []

    # 지역
    if region:
        parts.append(region + "에")

    # 거래 유형 + 가격
    if deal_type in ["매매"]:
        if dep_max > 0:
            price_str = f"{dep_max//10000}억원" if dep_max >= 10000 else f"{dep_max}만원"
            parts.append(f"{price_str} 이하 {prop_type}")
        else:
            parts.append(f"{prop_type}")
    elif deal_type == "전세":
        if dep_max > 0:
            price_str = f"{dep_max//10000}억" if dep_max >= 10000 else f"{dep_max}만원"
            if dep_min > 0:
                min_str = f"{dep_min//10000}억" if dep_min >= 10000 else f"{dep_min}만원"
                parts.append(f"전세 {min_str}~{price_str}짜리 {prop_type}")
            else:
                parts.append(f"전세 {price_str}짜리 {prop_type}")
        else:
            parts.append(f"전세 {prop_type}")
    elif deal_type in ["월세", "반전세"]:
        dep_str = f"보증금 {dep_max//10000}억" if dep_max >= 10000 else f"보증금 {dep_max}만원" if dep_max > 0 else ""
        mon_str = f"월세 {monthly_max}만원 이하" if monthly_max > 0 else ""
        price_part = " ".join(filter(None, [dep_str, mon_str]))
        parts.append(f"{price_part} {prop_type}" if price_part else prop_type)

    # 면적
    if area_min > 0 and area_max > 0:
        parts.append(f"전용 {area_min:.0f}~{area_max:.0f}㎡ ({area_min/3.3058:.0f}~{area_max/3.3058:.0f}평)")
    elif area_max > 0:
        parts.append(f"전용 {area_max:.0f}㎡ 이하")

    # 조건
    cond_map = {
        "역세권 필수": "역세권",
        "학군 필수": "학군 좋은",
        "주차 필수": "주차 가능한",
        "풀옵션 선호": "풀옵션",
        "신축 선호": "신축",
        "즉시 입주 가능": "즉시 입주 가능한",
        "대출 가능 필수": "대출 가능한",
    }
    cond_words = [cond_map[c] for c in conditions if c in cond_map]
    if cond_words:
        parts.append(" ".join(cond_words))

    parts.append("매물 찾아줘")

    return " ".join(parts) if parts else "조건에 맞는 매물 찾아줘"


def build_naver_url(region: str, prop_type: str, deal_type: str) -> str:
    """네이버 부동산 검색 URL 생성"""
    # 네이버 부동산 검색 기본 URL (지역명으로 검색)
    if region:
        encoded = urllib.parse.quote(region)
        return f"https://land.naver.com/search/index.naver?query={encoded}"
    return NAVER_LAND_BASE


# ─────────────────────────────────────────────
def render_intro():
    """상단 소개 배너"""
    st.markdown("""
    <div style="background:linear-gradient(135deg, #03c75a, #00b04f);
                border-radius:16px; padding:24px 28px; margin-bottom:20px; color:white;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
            <span style="font-size:2rem;">🟢</span>
            <div>
                <h2 style="margin:0; color:white; font-size:1.5rem;">
                    네이버 Pay AI 집찾기 × 롯데타워 AI 연동 센터
                </h2>
                <p style="margin:4px 0 0 0; font-size:0.9rem; opacity:0.9;">
                    Npay AI 집찾기의 강력한 자연어 검색을 우리 앱 수요 조건과 연결합니다
                </p>
            </div>
        </div>
    </div>

    <div style="display:flex; gap:12px; margin-bottom:20px;">
        <div style="flex:1; background:#0f172a; border:1px solid #1e3a2e; border-radius:12px;
                    padding:16px; text-align:center;">
            <div style="font-size:1.5rem;">🤖</div>
            <div style="color:#4ade80; font-weight:bold; margin:6px 0 4px;">AI 자연어 검색</div>
            <div style="color:#64748b; font-size:0.8rem;">조건 → 자연어 쿼리 자동 생성</div>
        </div>
        <div style="flex:1; background:#0f172a; border:1px solid #1e3a2e; border-radius:12px;
                    padding:16px; text-align:center;">
            <div style="font-size:1.5rem;">🔗</div>
            <div style="color:#4ade80; font-weight:bold; margin:6px 0 4px;">딥링크 연결</div>
            <div style="color:#64748b; font-size:0.8rem;">네이버 부동산 직접 연결</div>
        </div>
        <div style="flex:1; background:#0f172a; border:1px solid #1e3a2e; border-radius:12px;
                    padding:16px; text-align:center;">
            <div style="font-size:1.5rem;">📱</div>
            <div style="color:#4ade80; font-weight:bold; margin:6px 0 4px;">Npay 앱 QR</div>
            <div style="color:#64748b; font-size:0.8rem;">앱 설치 후 1,000P 즉시 적립</div>
        </div>
        <div style="flex:1; background:#0f172a; border:1px solid #1e3a2e; border-radius:12px;
                    padding:16px; text-align:center;">
            <div style="font-size:1.5rem;">🛡️</div>
            <div style="color:#4ade80; font-weight:bold; margin:6px 0 4px;">피싱 사기 예방</div>
            <div style="color:#64748b; font-size:0.8rem;">Npay 앱 악성 앱 자동 차단</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_query_generator():
    """수요 조건 → 네이버 AI 자연어 쿼리 생성기"""
    st.markdown("### 🤖 AI 자연어 쿼리 자동 생성기")
    st.caption("아래 조건을 입력하면 → 네이버 AI 집찾기에 바로 붙여넣을 수 있는 자연어 문장을 생성합니다.")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        region   = col1.text_input("🏘️ 희망 지역 (동/구 단위)",
                                    placeholder="예: 강남구 대치동, 분당구 정자동",
                                    key="nav_region")
        prop_type = col2.selectbox("🏠 매물 종류",
                                    list(PROP_TYPES_MAP.keys()), key="nav_prop")

        col3, col4 = st.columns(2)
        deal_type = col3.selectbox("💳 거래 구분",
                                    list(DEAL_MAP.keys()), key="nav_deal")
        conditions = col4.multiselect("✅ 필수 조건",
                                       ["역세권 필수", "학군 필수", "주차 필수",
                                        "풀옵션 선호", "신축 선호", "즉시 입주 가능",
                                        "대출 가능 필수"], key="nav_conds")

        st.markdown("**💰 가격 범위**")
        pc1, pc2, pc3, pc4 = st.columns(4)
        dep_min    = pc1.number_input("보증금 하한 (만원)", min_value=0, step=1000, key="nav_dep_min")
        dep_max    = pc2.number_input("보증금 상한 (만원)", min_value=0, step=1000, key="nav_dep_max")
        mon_min    = pc3.number_input("월세 하한 (만원)",  min_value=0, step=10,   key="nav_mon_min")
        mon_max    = pc4.number_input("월세 상한 (만원)",  min_value=0, step=10,   key="nav_mon_max")
        if dep_max > 0: pc2.caption(f"≈ {dep_max/10000:.2f}억")

        st.markdown("**📐 면적 범위 (전용)**")
        ac1, ac2, ac3, ac4 = st.columns(4)
        area_min = ac1.number_input("최소 (㎡)", min_value=0.0, step=1.0, key="nav_area_min")
        area_max = ac2.number_input("최대 (㎡)", min_value=0.0, step=1.0, key="nav_area_max")
        if area_min > 0: ac3.caption(f"≈ {area_min/3.3058:.1f}평")
        if area_max > 0: ac4.caption(f"≈ {area_max/3.3058:.1f}평")

        st.markdown("---")
        generate_btn = st.button("🤖 네이버 AI 집찾기 쿼리 자동 생성",
                                  type="primary", use_container_width=True,
                                  key="nav_gen_btn")

    if generate_btn or st.session_state.get("nav_query"):
        deal_kr = DEAL_MAP.get(deal_type, deal_type)
        prop_kr = PROP_TYPES_MAP.get(prop_type, prop_type)
        query   = build_naver_query(
            region, prop_kr, deal_kr,
            area_min, area_max,
            dep_min, dep_max, mon_min, mon_max,
            conditions
        )
        st.session_state["nav_query"] = query

        naver_url = build_naver_url(region, prop_kr, deal_kr)

        st.markdown("""
        <div style="background:#0f172a; border:2px solid #03c75a; border-radius:12px;
                    padding:20px; margin-top:16px;">
            <div style="color:#4ade80; font-size:0.85rem; margin-bottom:8px;">
                ✅ 생성된 네이버 AI 집찾기 자연어 쿼리
            </div>
        """, unsafe_allow_html=True)

        st.code(query, language=None)

        st.markdown("""
        <div style="color:#94a3b8; font-size:0.8rem; margin-top:8px;">
            💡 위 문장을 복사하여 <b style="color:#03c75a;">Npay 앱 → AI 집찾기</b>에 붙여넣으세요!
        </div></div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        cc1, cc2 = st.columns(2)
        cc1.link_button(
            "🟢 네이버 부동산에서 매물 검색",
            naver_url,
            use_container_width=True,
            type="primary",
        )
        cc2.link_button(
            "📱 Npay AI 집찾기 캠페인 바로가기",
            NAVER_AI_CAMPAIGN,
            use_container_width=True,
        )

        # 조건 요약 표시
        st.markdown("#### 📋 입력 조건 요약")
        summary_cols = st.columns(4)
        summary_cols[0].metric("지역", region if region else "미입력")
        summary_cols[1].metric("매물종류", f"{prop_type} ({deal_kr})")
        summary_cols[2].metric("보증금 범위",
                                f"{dep_min//10000}억~{dep_max//10000}억" if dep_max > 0 else "미입력")
        summary_cols[3].metric("면적 범위",
                                f"{area_min:.0f}~{area_max:.0f}㎡" if area_max > 0 else "미입력")


def render_npay_info():
    """Npay AI 집찾기 소개 + QR 코드"""
    st.markdown("---")
    st.markdown("### 📱 Npay AI 집찾기 주요 기능")

    ic1, ic2, ic3 = st.columns(3)

    with ic1:
        st.markdown("""
        <div style="background:#0f172a; border:1px solid #1e3a2e; border-radius:12px; padding:20px; height:180px;">
            <div style="font-size:1.8rem; text-align:center;">🤖</div>
            <h4 style="color:#4ade80; text-align:center; margin:8px 0;">AI 집찾기</h4>
            <p style="color:#94a3b8; font-size:0.82rem; text-align:center;">
                "정자동에 전세 3억짜리<br>채광 좋은 오피스텔 찾아줘"<br>
                자연어로 바로 검색!
            </p>
        </div>
        """, unsafe_allow_html=True)

    with ic2:
        st.markdown("""
        <div style="background:#0f172a; border:1px solid #1e3a2e; border-radius:12px; padding:20px; height:180px;">
            <div style="font-size:1.8rem; text-align:center;">🏠</div>
            <h4 style="color:#4ade80; text-align:center; margin:8px 0;">시작화면 설정</h4>
            <p style="color:#94a3b8; font-size:0.82rem; text-align:center;">
                Npay 앱 시작화면으로<br>부동산 설정 가능<br>
                1초 컷으로 확인!
            </p>
        </div>
        """, unsafe_allow_html=True)

    with ic3:
        st.markdown("""
        <div style="background:#0f172a; border:1px solid #1e3a2e; border-radius:12px; padding:20px; height:180px;">
            <div style="font-size:1.8rem; text-align:center;">🛡️</div>
            <h4 style="color:#4ade80; text-align:center; margin:8px 0;">피싱 사기 예방</h4>
            <p style="color:#94a3b8; font-size:0.82rem; text-align:center;">
                Npay 앱 켜기만 해도<br>악성 앱·피싱 사기로부터<br>자동 보호!
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎁 현재 진행 중인 이벤트")

    ev1, ev2 = st.columns(2)
    with ev1:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1e3a1e,#0f2a0f);
                    border:1px solid #03c75a; border-radius:12px; padding:20px; text-align:center;">
            <div style="font-size:2rem;">🎯</div>
            <h4 style="color:#4ade80; margin:8px 0;">이벤트 1</h4>
            <p style="color:#f8fafc; font-size:1rem; font-weight:bold;">
                AI 집찾기 체험하고<br>포인트 <span style="color:#fbbf24;">1만원</span> 받으세요
            </p>
            <p style="color:#94a3b8; font-size:0.8rem;">
                추첨 100명 · Npay 포인트 1만원
            </p>
        </div>
        """, unsafe_allow_html=True)

    with ev2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1e3a1e,#0f2a0f);
                    border:1px solid #03c75a; border-radius:12px; padding:20px; text-align:center;">
            <div style="font-size:2rem;">📲</div>
            <h4 style="color:#4ade80; margin:8px 0;">이벤트 2</h4>
            <p style="color:#f8fafc; font-size:1rem; font-weight:bold;">
                앱 첫 설치하면<br>포인트 <span style="color:#fbbf24;">1천원</span> 즉시 적립
            </p>
            <p style="color:#94a3b8; font-size:0.8rem;">
                생애 첫 설치 + 본인인증 완료 시
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔗 바로 이동하기")

    lc1, lc2, lc3 = st.columns(3)
    lc1.link_button("📱 Npay AI 집찾기 캠페인",
                    NAVER_AI_CAMPAIGN, use_container_width=True, type="primary")
    lc2.link_button("🏠 네이버 부동산 바로가기",
                    NAVER_LAND_BASE, use_container_width=True)
    lc3.link_button("🗺️ 네이버 지도 부동산",
                    "https://map.naver.com/", use_container_width=True)


def render_synergy():
    """우리 앱 + 네이버 AI 시너지 전략"""
    st.markdown("---")
    st.markdown("### ⚡ 롯데타워 AI × 네이버 AI 시너지 활용법")

    st.markdown("""
    <div style="background:#0f172a; border-radius:12px; padding:20px; margin-bottom:16px;">
        <table style="width:100%; border-collapse:collapse; color:#e2e8f0; font-size:0.88rem;">
            <thead>
                <tr style="background:#1e293b;">
                    <th style="padding:10px; text-align:left; color:#4ade80;">단계</th>
                    <th style="padding:10px; text-align:left; color:#4ade80;">롯데타워 AI 앱 (우리)</th>
                    <th style="padding:10px; text-align:left; color:#4ade80;">네이버 Pay AI 집찾기</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:10px;">🔍 1단계<br><small>매물 탐색</small></td>
                    <td style="padding:10px;">수요자 상세 조건 입력<br><small>면적·가격·층수·특징 선택</small></td>
                    <td style="padding:10px;">자연어 쿼리로 광범위 검색<br><small>"대치동 전세 5억 아파트 찾아줘"</small></td>
                </tr>
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:10px;">🤝 2단계<br><small>공동중개</small></td>
                    <td style="padding:10px;">강남구 1,500개 부동산 공동중개<br><small>비공개 급매물 48시간 선점</small></td>
                    <td style="padding:10px;">네이버 공개 매물 실거래 확인<br><small>시세 비교 및 가격 검증</small></td>
                </tr>
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:10px;">📊 3단계<br><small>AI 분석</small></td>
                    <td style="padding:10px;">AI 매칭 점수(94/100) 제공<br><small>학군·입지·실거래 분석</small></td>
                    <td style="padding:10px;">자연어 조건 파싱 + 매물 필터링<br><small>남향·채광·층수 자동 반영</small></td>
                </tr>
                <tr>
                    <td style="padding:10px;">✅ 4단계<br><small>계약 성사</small></td>
                    <td style="padding:10px;">공급자-수요자 AI 매칭 완료<br><small>나노 바나나 CEO 숏츠 마케팅</small></td>
                    <td style="padding:10px;">Npay 결제 연동<br><small>피싱 사기 예방 보호</small></td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 **Best Practice**: 우리 앱으로 공동중개망 비공개 매물을 먼저 확인 → 네이버 AI로 시세·공개 매물 교차 검증 → 최종 계약 진행")


# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="네이버 AI 집찾기 연동",
        page_icon="🟢",
        layout="wide"
    )

    render_intro()

    tab1, tab2, tab3 = st.tabs([
        "🤖 AI 쿼리 자동 생성기",
        "📱 Npay AI 집찾기 안내",
        "⚡ 시너지 활용 전략"
    ])

    with tab1:
        render_query_generator()

    with tab2:
        render_npay_info()

    with tab3:
        render_synergy()


if __name__ == "__main__":
    main()
else:
    # app.py 등에서 import 후 직접 호출 시
    render_intro()
    tab1, tab2, tab3 = st.tabs([
        "🤖 AI 쿼리 자동 생성기",
        "📱 Npay AI 집찾기 안내",
        "⚡ 시너지 활용 전략"
    ])
    with tab1:
        render_query_generator()
    with tab2:
        render_npay_info()
    with tab3:
        render_synergy()
