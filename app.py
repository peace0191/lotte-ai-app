import streamlit as st
import pandas as pd
import random
import time
import datetime


# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="롯데타워앤강남빌딩 AI 부동산",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "nav_target" not in st.session_state:
    st.session_state["nav_target"] = None


# =========================
# UI 스타일
# =========================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}

.stApp {
    background: #f8fafc !important;
}

.block-container {
    max-width: 1200px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 110px !important;
}

h1, h2, h3, h4 {
    color: #0f172a !important;
    font-weight: 800 !important;
}

p, li, span, label, div {
    color: #334155;
    line-height: 1.7;
}

.stButton > button {
    min-height: 46px;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 800 !important;
}

input, textarea {
    font-size: 16px !important;
}

.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    margin-bottom: 14px;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
}

.metric-title {
    color: #64748b;
    font-size: 0.88rem;
    font-weight: 700;
    margin-bottom: 4px;
}

.metric-value {
    color: #0f172a;
    font-size: 1.9rem;
    font-weight: 900;
    line-height: 1.2;
}

.metric-sub {
    color: #475569;
    font-size: 0.82rem;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 900;
    color: #0f172a;
    margin: 8px 0 14px 0;
}

.subtle {
    color: #64748b;
    font-size: 0.92rem;
}

.bottom-nav-wrap {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 99999;
    background: rgba(255,255,255,0.96);
    border-top: 1px solid #e2e8f0;
    box-shadow: 0 -8px 24px rgba(15, 23, 42, 0.06);
    padding: 10px 12px;
}

.bottom-nav-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    max-width: 1200px;
    margin: 0 auto;
}

.nav-note {
    color: #64748b;
    font-size: 13px;
}

header, footer {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# 공통 헬퍼
# =========================
def go_tab(tab_name: str) -> None:
    st.session_state["nav_target"] = tab_name
    st.rerun()


def render_metric(title: str, value: str, sub: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_property_card(title: str, price: str, desc: str, tag: str = "") -> None:
    badge = (
        f'<div style="display:inline-block;background:#eff6ff;color:#2563eb;border:1px solid #bfdbfe;'
        f'padding:4px 10px;border-radius:999px;font-size:12px;font-weight:800;margin-bottom:10px;">{tag}</div>'
        if tag
        else ""
    )
    st.markdown(
        f"""
        <div class="card">
            {badge}
            <div style="font-size:1.08rem;font-weight:900;color:#0f172a;">{title}</div>
            <div style="font-size:1.45rem;font-weight:900;color:#1d4ed8;margin-top:6px;">{price}</div>
            <div style="font-size:0.95rem;color:#475569;margin-top:10px;line-height:1.7;">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# 로그인 화면
# =========================
def render_login_page() -> None:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #061537 0%, #081a45 100%);
            color: #ffffff;
            padding: 34px;
            border-radius: 18px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(2, 6, 23, 0.22);
            border: 1px solid rgba(255,255,255,0.06);
        ">
            <div style="display:flex; align-items:flex-start; gap:18px; margin-bottom:18px;">
                <div style="
                    background:#fbbf24;
                    width:76px;
                    height:76px;
                    border-radius:50%;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:36px;
                    flex-shrink:0;
                    box-shadow:0 6px 18px rgba(251,191,36,0.35);
                ">👨‍💼</div>

                <div style="flex:1;">
                    <div style="font-size:1.35rem;font-weight:900;color:#f8fafc;line-height:1.45;">
                        롯데타워앤강남빌딩부동산중개주식회사
                    </div>
                    <div style="color:#cbd5e1;font-size:0.92rem;margin-top:6px;">
                        등록번호: 11680-2023-00078 | 사업자: 461-86-02740
                    </div>
                    <div style="font-size:1.55rem;color:#fbbf24;font-weight:900;margin-top:10px;">
                        대표: 공인중개사 이상수
                    </div>
                    <div style="color:#f1f5f9;font-size:1.03rem;font-weight:600;margin-top:8px;">
                        Tel: 02-578-8285 / 010-8985-8945
                    </div>
                </div>
            </div>

            <div style="color:#fde68a;font-size:1.55rem;font-weight:900;line-height:1.5;">
                대치1동은 자녀의 미래 베이스캠프입니다.
            </div>

            <div style="color:#e2e8f0;line-height:1.9;font-size:1.02rem;margin-top:14px;font-weight:500;">
                AI 저평가 분석과 예약 AI자동 매칭 시스템으로 숨겨진 부동산 가치를 발굴하고,<br>
                대한민국 최고의 교육 환경으로 가는 최적의 출발점을 찾아드립니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">🔷 AI 부동산 핵심 3대 전략</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown(
            """
            <div class="card">
                <div style="font-size:1rem;font-weight:900;color:#0f172a;">🎓 교육특구 1번지 분석</div>
                <div class="subtle" style="margin-top:8px;">
                    래대팰·SK뷰(대치초/단대부고) vs 아이파크(대도초/숙명여중고)<br>
                    학군 정밀 분석 및 배정 원칙 데이터화
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            """
            <div class="card">
                <div style="font-size:1rem;font-weight:900;color:#0f172a;">🧠 AI 저평가·예약 자동매칭</div>
                <div class="subtle" style="margin-top:8px;">
                    저평가 매물을 분석하고 수요·공급 조건을 빠르게 연결하여
                    거래 가능성을 높입니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown(
            """
            <div class="card">
                <div style="font-size:1rem;font-weight:900;color:#0f172a;">📣 AI 자동 홍보 시스템</div>
                <div class="subtle" style="margin-top:8px;">
                    매물 접수 즉시 홍보 문구, 브리핑 문장, 숏츠 소재를
                    자동으로 생성합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="card" style="background:linear-gradient(135deg,#0f172a,#1e3a5f); color:white;">
            <div style="font-size:1.08rem;font-weight:900;color:#fcd34d;">🏠 부동산 저평가 매물 & 사전예약 AI 자동매칭 플랫폼</div>
            <div style="margin-top:12px;color:#e2e8f0;">
                학군 이사 수요, 희소 매물, 입주 시기 불일치 문제를 AI가 분석하여
                더 빠르고 정확한 연결을 돕습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("### 📱 핸드폰 인증 로그인")
        name = st.text_input("이름", placeholder="예: 홍길동")
        phone = st.text_input("휴대폰 번호", placeholder="01012345678")

        if st.button("인증번호 발송 및 로그인", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("이름을 입력해주세요.")
            elif len(phone.strip()) < 10:
                st.error("휴대폰 번호를 올바르게 입력해주세요.")
            else:
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = name.strip()
                st.success(f"{name.strip()}님, 로그인되었습니다.")
                st.rerun()


# =========================
# 홈
# =========================
def render_home() -> None:
    st.markdown(
        f"""
        <div class="card" style="background:linear-gradient(135deg,#0f172a,#1e293b); color:white;">
            <div style="font-size:1.6rem;font-weight:900;color:#f8fafc;">🏠 대치1동 특성 및 AI 부동산 개요</div>
            <div style="margin-top:10px;color:#cbd5e1;font-size:1rem;">
                교육특구, 학군 프리미엄, 실거래 기반 AI 분석을 결합한
                대치1동 맞춤형 부동산 안내 화면입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric("20평형대 평균가", "23.5억", "실거래·매물 종합")
    with c2:
        render_metric("30평형대 평균가", "32.5억", "국민평형 중심")
    with c3:
        render_metric("40평형대 평균가", "48.0억", "대형 평형 추정")

    st.markdown('<div class="section-title">🎓 통합 교육환경 요약</div>', unsafe_allow_html=True)
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        st.markdown(
            """
            <div class="card">
                <div style="font-weight:900;">🏫 초등학교</div>
                <div class="subtle" style="margin-top:8px;">대치초, 대도초</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ec2:
        st.markdown(
            """
            <div class="card">
                <div style="font-weight:900;">🏫 중학교</div>
                <div class="subtle" style="margin-top:8px;">대청중, 숙명여중</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ec3:
        st.markdown(
            """
            <div class="card">
                <div style="font-weight:900;">🏫 고등학교</div>
                <div class="subtle" style="margin-top:8px;">단대부고, 숙명여고</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">🏘️ 주요 단지 분석</div>', unsafe_allow_html=True)
    tabs = st.tabs(["래미안대치팰리스", "대치SK뷰", "대치아이파크", "은마아파트"])
    with tabs[0]:
        st.info("대치동 대표 대장주 단지. 학군·학원가·주거 선호도가 높은 핵심 단지입니다.")
    with tabs[1]:
        st.info("역세권과 실거주 편의성이 강점인 인기 단지입니다.")
    with tabs[2]:
        st.info("대도초·숙명 라인 선호 수요와 함께 실거주 만족도가 높은 단지입니다.")
    with tabs[3]:
        st.info("재건축 상징성과 투자 수요가 높은 대표 단지입니다.")


# =========================
# 추천매물
# =========================
def render_listing() -> None:
    st.markdown('<div class="section-title">⭐ AI 저평가 추천매물</div>', unsafe_allow_html=True)
    st.caption("실거래 흐름, 입지, 학군, 희소성을 종합해 예시 추천한 데모 화면입니다.")

    c1, c2 = st.columns(2)
    with c1:
        render_property_card(
            "래미안대치팰리스 34평 남향",
            "40.5억",
            "대치초 배정권, 중층, 남향, 학원가 접근성 우수. 최근 기준 시세 대비 매력적인 조건.",
            "AI 저평가"
        )
    with c2:
        render_property_card(
            "대치SK뷰 33평 전세",
            "14.5억",
            "대치역 접근성, 실거주 선호, 가족 수요 적합. 입주 일정 유연.",
            "전세 추천"
        )

    c3, c4 = st.columns(2)
    with c3:
        render_property_card(
            "시그니엘 레지던스 88평",
            "63.8억",
            "고층, 뷰 우수, 프리미엄 자산가 수요 맞춤형.",
            "프리미엄"
        )
    with c4:
        render_property_card(
            "은마아파트 31평 월세",
            "5천 / 185만",
            "재건축 기대감, 대치동 중심 입지, 실사용 및 투자 관심 병행.",
            "월세 추천"
        )


# =========================
# AI 매칭 / 예약
# =========================
def render_matching() -> None:
    st.markdown('<div class="section-title">🤖 AI 매칭 / 사전등록</div>', unsafe_allow_html=True)
    st.caption("공급자와 수요자의 조건을 빠르게 받아 AI 매칭을 위한 기초 데이터를 수집합니다.")

    tab1, tab2 = st.tabs(["공급자 등록", "수요자 등록"])

    with tab1:
        with st.form("supply_form"):
            name = st.text_input("이름", key="supply_name")
            phone = st.text_input("연락처", key="supply_phone")
            prop = st.selectbox("매물 종류", ["아파트", "오피스텔", "상가", "기타"], key="supply_prop")
            trade = st.selectbox("거래 구분", ["매매", "전세", "월세"], key="supply_trade")
            complex_name = st.text_input("단지명/건물명", key="supply_complex")
            memo = st.text_area("특이사항", key="supply_memo")
            submitted = st.form_submit_button("공급 등록", use_container_width=True, type="primary")

            if submitted:
                if not name or not phone or not complex_name:
                    st.error("이름, 연락처, 단지명은 필수입니다.")
                else:
                    st.success("공급자 등록이 완료되었습니다.")
                    st.json(
                        {
                            "이름": name,
                            "연락처": phone,
                            "매물종류": prop,
                            "거래구분": trade,
                            "단지명": complex_name,
                            "특이사항": memo,
                            "접수시각": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

    with tab2:
        with st.form("demand_form"):
            name = st.text_input("이름", key="demand_name")
            phone = st.text_input("연락처", key="demand_phone")
            region = st.text_input("희망 지역", key="demand_region")
            budget = st.text_input("예산", key="demand_budget")
            condition = st.text_area("희망 조건", key="demand_condition")
            submitted = st.form_submit_button("수요 등록", use_container_width=True, type="primary")

            if submitted:
                if not name or not phone or not region:
                    st.error("이름, 연락처, 희망 지역은 필수입니다.")
                else:
                    st.success("수요자 등록이 완료되었습니다.")
                    st.json(
                        {
                            "이름": name,
                            "연락처": phone,
                            "희망지역": region,
                            "예산": budget,
                            "희망조건": condition,
                            "접수시각": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

    st.markdown("---")
    st.markdown("### 💬 AI 챗봇 데모")
    prompt = st.text_input("질문을 입력하세요", placeholder="예: 대치동 34평 최근 시세는?")
    if st.button("AI 답변 보기", key="chat_demo_btn"):
        if not prompt:
            st.warning("질문을 입력해주세요.")
        else:
            st.info(f"'{prompt}'에 대한 데모 답변입니다. 실제 서비스에서는 실거래·매물 데이터와 연결됩니다.")


# =========================
# 하단 버튼
# =========================
def render_bottom_nav() -> None:
    st.markdown('<div class="bottom-nav-wrap"><div class="bottom-nav-grid">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📤 공유하기", use_container_width=True):
            st.info("공유 기능은 다음 단계에서 연결할 수 있습니다.")
    with col2:
        if st.button("🔷 AI핵심 3대전략", use_container_width=True):
            go_tab("home")
    with col3:
        if st.button("🤖 AI 매칭 가기", use_container_width=True):
            go_tab("matching")
    st.markdown("</div></div>", unsafe_allow_html=True)


# =========================
# 메인
# =========================
def main() -> None:
    st.sidebar.header("🔗 앱 안내")
    st.sidebar.success("https://lotte-ai-app.streamlit.app")
    st.sidebar.caption("현재는 안정화 버전 app.py 입니다.")

    if not st.session_state["logged_in"]:
        render_login_page()
        render_bottom_nav()
        return

    tab_order = ["home", "listing", "matching"]
    if st.session_state["nav_target"] in tab_order:
        chosen = st.session_state["nav_target"]
    else:
        chosen = "home"

    titles = {
        "home": "🏠 대치1동 특성",
        "listing": "⭐ AI추천매물",
        "matching": "🤖 AI매칭/사전등록",
    }

    tabs = st.tabs([titles[k] for k in tab_order])

    for idx, key in enumerate(tab_order):
        with tabs[idx]:
            if key == "home":
                render_home()
            elif key == "listing":
                render_listing()
            elif key == "matching":
                render_matching()

    render_bottom_nav()


if __name__ == "__main__":
    main()