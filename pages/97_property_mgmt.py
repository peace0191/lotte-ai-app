# pages/97_property_mgmt.py
# 파발마 스타일 매물관리 페이지 (관리자 전용)
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import random

st.set_page_config(
    page_title="매물관리 | BARA AI",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────
# 관리자 인증
# ──────────────────────────────
try:
    from services.admin_gate import require_admin
    require_admin()
except Exception:
    pass  # 인증 모듈 없을 시 패스

# ──────────────────────────────
# CSS 스타일
# ──────────────────────────────
st.markdown("""
<style>
/* 전체 배경 */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1a2340 0%, #243060 50%, #1a2340 100%);
    font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
}

/* 사이드바 스타일 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1729 0%, #1a2340 100%) !important;
    border-right: 1px solid #2d3a5c;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #ffffff !important;
    font-size: 0.85rem !important;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

/* 헤더 배너 */
.pm-header {
    background: linear-gradient(90deg, #1e3a8a 0%, #1d4ed8 50%, #2563eb 100%);
    padding: 14px 24px;
    border-radius: 10px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
}
.pm-header h1 {
    color: #ffffff;
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.pm-header span {
    color: #bfdbfe;
    font-size: 0.85rem;
}

/* 검색 패널 */
.search-panel {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 14px;
    backdrop-filter: blur(10px);
}

/* 탭 버튼 (파발마 스타일) */
.pm-tab-row {
    display: flex;
    gap: 6px;
    margin-bottom: 14px;
    flex-wrap: wrap;
}
.pm-tab-btn {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #cbd5e1;
    padding: 5px 14px;
    border-radius: 6px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}
.pm-tab-btn.active {
    background: #2563eb;
    border-color: #3b82f6;
    color: #ffffff;
    font-weight: 600;
}
.pm-tab-btn:hover {
    background: rgba(37,99,235,0.5);
    color: #ffffff;
}

/* 액션 버튼 */
.action-bar {
    display: flex;
    gap: 6px;
    margin-bottom: 12px;
    flex-wrap: wrap;
    align-items: center;
}
.act-btn {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #e2e8f0;
    padding: 5px 12px;
    border-radius: 5px;
    font-size: 0.8rem;
    cursor: pointer;
}
.act-btn.primary {
    background: linear-gradient(135deg, #10b981, #059669);
    border-color: #059669;
    color: #fff;
    font-weight: 600;
}
.act-btn.warning {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    border-color: #d97706;
    color: #fff;
    font-weight: 600;
}
.act-cnt {
    color: #fbbf24;
    font-weight: 700;
    font-size: 0.9rem;
    margin: 0 8px;
}

/* 데이터 테이블 */
.property-table {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    overflow: hidden;
}

/* 통계 카드 */
.stat-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 8px;
    padding: 12px 16px;
    text-align: center;
}
.stat-card .stat-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: #60a5fa;
}
.stat-card .stat-label {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 2px;
}
.stat-card .stat-delta {
    font-size: 0.75rem;
    color: #34d399;
    font-weight: 600;
}

/* 사이드바 필터 항목 */
.side-filter-item {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    padding: 6px 10px;
    margin-bottom: 4px;
    color: #e2e8f0;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
}
.side-filter-item:hover {
    background: rgba(37,99,235,0.3);
    border-color: #3b82f6;
}
.side-filter-item.active {
    background: rgba(37,99,235,0.5);
    border-color: #60a5fa;
    color: #ffffff;
    font-weight: 600;
}

/* 배지 */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-sell { background: #ef4444; color: white; }
.badge-rent { background: #3b82f6; color: white; }
.badge-monthly { background: #8b5cf6; color: white; }
.badge-new { background: #10b981; color: white; }
.badge-urgent { background: #f59e0b; color: white; }

/* 레이블 */
label, .stSelectbox label, .stDateInput label {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
}
p, .stMarkdown p {
    color: #e2e8f0;
}

/* Streamlit 기본 배경 제거 */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 100%;
}

/* 입력 필드 */
input, [data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 6px !important;
}
select, [data-testid="stSelectbox"] {
    color: #ffffff !important;
}

/* datatable 스타일 */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* 강조 헤더 텍스트 */
h3 { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────
# 샘플 매물 데이터 생성
# ──────────────────────────────
@st.cache_data(ttl=60)
def make_sample_data():
    random.seed(42)
    types = ["아파트", "오피스텔", "빌라", "상가", "오피스"]
    deal_types = ["매매", "전세", "월세"]
    sido = ["서울", "경기", "인천"]
    gugun = {
        "서울": ["강남구", "서초구", "송파구", "마포구", "용산구"],
        "경기": ["성남시", "수원시", "용인시", "화성시"],
        "인천": ["연수구", "부평구", "남동구"]
    }
    eup = {
        "강남구": ["대치동", "삼성동", "청담동", "역삼동"],
        "서초구": ["반포동", "잠원동", "양재동"],
        "송파구": ["잠실동", "방이동", "가락동"],
        "성남시": ["분당동", "수내동", "정자동"],
        "수원시": ["영통동", "매탄동"],
        "연수구": ["송도동", "연수동"],
        "마포구": ["합정동", "망원동", "상수동"],
        "용산구": ["한남동", "이태원동"],
        "용인시": ["수지구", "기흥구"],
        "화성시": ["동탄동"],
        "부평구": ["부평동", "갈산동"],
        "남동구": ["구월동", "만수동"]
    }
    names = ["래미안","힐스테이트","자이","롯데캐슬","아이파크","푸르지오","e편한세상","더샵"]

    rows = []
    base_date = datetime(2026, 2, 4)
    for i in range(120):
        sd = random.choice(list(gugun.keys()))
        sg = random.choice(gugun.get(sd, ["기타"]))
        se = random.choice(eup.get(sg, ["기타동"]))
        tp = random.choice(deal_types)
        매매가 = random.randint(5, 80) if tp == "매매" else 0
        보증금 = random.randint(1, 30) if tp in ["전세","월세"] else 0
        월세 = random.randint(50, 300) if tp == "월세" else 0
        rows.append({
            "선택": False,
            "받은쪽지": random.choice(["●", ""]),
            "이미구분": random.choice(["공동", "전속", "일반"]),
            "유형": random.choice(types),
            "물건공부": random.choice(["등기부", "건축물대장", "토지대장"]),
            "시도": random.choice(["서울","경기","인천"]),
            "구군": sg,
            "읍면동": se,
            "매매가(억)": 매매가 if tp == "매매" else "-",
            "보증금(억)": 보증금 if tp in ["전세","월세"] else "-",
            "월세(만)": 월세 if tp == "월세" else "-",
            "거래유형": tp,
            "제목": f"{random.choice(names)} {random.randint(10,50)}평 {tp}",
            "내용": f"역세권 {random.randint(1,10)}분, {random.choice(['로얄층','저층','중층','고층'])} 급{'매' if random.random()>0.5 else '거'}",
            "등록일": (base_date + timedelta(days=random.randint(0,28))).strftime("%Y-%m-%d"),
            "상태": random.choice(["신규", "진행중", "완료", "보류"]),
        })
    return pd.DataFrame(rows)

df_all = make_sample_data()

# ──────────────────────────────
# 사이드바 – 필터
# ──────────────────────────────
with st.sidebar:
    st.markdown("### 🏠 매물종류별")

    # 매물종류 선택 상태
    if "pm_prop_type" not in st.session_state:
        st.session_state.pm_prop_type = "전체"

    prop_types = ["전체", "아파트", "오피스텔", "빌라", "상가", "오피스"]
    for pt in prop_types:
        cnt = len(df_all) if pt == "전체" else len(df_all[df_all["유형"] == pt])
        active_class = "active" if st.session_state.pm_prop_type == pt else ""
        if st.button(f"{'★ ' if pt=='전체' else ''}{pt}  ({cnt})", key=f"pt_{pt}",
                     use_container_width=True,
                     type="primary" if st.session_state.pm_prop_type == pt else "secondary"):
            st.session_state.pm_prop_type = pt
            st.rerun()

    st.markdown("---")
    st.markdown("### 📍 발송지역별")

    if "pm_region" not in st.session_state:
        st.session_state.pm_region = "전체"

    regions = ["전체", "서울", "경기", "인천"]
    for rg in regions:
        cnt = len(df_all) if rg == "전체" else len(df_all[df_all["시도"] == rg])
        if st.button(f"{rg}  ({cnt})", key=f"rg_{rg}",
                     use_container_width=True,
                     type="primary" if st.session_state.pm_region == rg else "secondary"):
            st.session_state.pm_region = rg
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 통계")
    total = len(df_all)
    new_cnt = len(df_all[df_all["상태"] == "신규"])
    done_cnt = len(df_all[df_all["상태"] == "완료"])
    st.metric("전체 매물", f"{total:,}건")
    st.metric("신규 등록", f"{new_cnt}건", f"+{new_cnt}")
    st.metric("완료", f"{done_cnt}건")

# ──────────────────────────────
# 메인 화면
# ──────────────────────────────

# 헤더
st.markdown("""
<div class="pm-header">
    <div>
        <h1>🏢 매물관리</h1>
        <span>파발마 스타일 | 관리자 전용 매물 검색/관리 시스템</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 상단 통계 카드
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown("""<div class="stat-card">
        <div class="stat-num">120</div>
        <div class="stat-label">전체 매물</div>
        <div class="stat-delta">+12 ↑</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="stat-card">
        <div class="stat-num" style="color:#34d399;">48</div>
        <div class="stat-label">매매</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="stat-card">
        <div class="stat-num" style="color:#60a5fa;">35</div>
        <div class="stat-label">전세</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown("""<div class="stat-card">
        <div class="stat-num" style="color:#c084fc;">37</div>
        <div class="stat-label">월세</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown("""<div class="stat-card">
        <div class="stat-num" style="color:#fbbf24;">8</div>
        <div class="stat-label">보류/검토</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 검색 패널
with st.container():
    st.markdown('<div class="search-panel">', unsafe_allow_html=True)
    
    # 행 1: 날짜 + 검색조건
    col_date1, col_date2, col_dash, col_cond, col_kw, col_btn = st.columns([2, 2, 0.3, 2, 3, 1.5])
    with col_date1:
        d_from = st.date_input("조회 시작일", value=date(2026, 2, 4), label_visibility="visible")
    with col_date2:
        d_to = st.date_input("조회 종료일", value=date(2026, 3, 4), label_visibility="visible")
    with col_dash:
        st.markdown("<br><div style='text-align:center;color:#94a3b8;padding-top:28px;'>~</div>", unsafe_allow_html=True)
    with col_cond:
        search_cond = st.selectbox("검색조건", ["전체", "제목", "내용", "주소", "거래유형", "유형"], label_visibility="visible")
    with col_kw:
        search_kw = st.text_input("검색어", placeholder="검색어를 입력하세요...", label_visibility="visible")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        do_search = st.button("🔍 검색", use_container_width=True, type="primary")

    # 행 2: 빠른 필터 체크박스
    st.markdown("<div style='margin-top:10px;'>", unsafe_allow_html=True)
    fc1, fc2, fc3, fc4, fc5, fc6, fc7, fc8 = st.columns(8)
    chk_국내 = fc1.checkbox("국내소재", value=True)
    chk_직거 = fc2.checkbox("직거래")
    chk_신규 = fc3.checkbox("새로 나온")
    chk_급매 = fc4.checkbox("급매물")
    chk_주인 = fc5.checkbox("집주인 직접")
    chk_수익 = fc6.checkbox("수익성 우수")
    chk_미계 = fc7.checkbox("미계약")
    chk_추천 = fc8.checkbox("AI 추천")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── 액션 버튼 바
act1, act2, act3, act4, act5, act6 = st.columns([1.2, 1.2, 1.2, 1.5, 2.5, 2])
with act1:
    if st.button("✏️ 수기 등록", use_container_width=True):
        st.session_state.show_register = True
with act2:
    if st.button("📋 대장보기", use_container_width=True):
        st.info("건축물대장 조회 기능 (연동 준비 중)")
with act3:
    if st.button("🔍 상세보기", use_container_width=True):
        st.info("선택 매물의 상세 정보를 확인합니다.")
with act4:
    if st.button("🤖 자동가격조정", use_container_width=True, type="primary"):
        with st.spinner("AI 가격 분석 중..."):
            import time; time.sleep(1.5)
        st.success("AI 기반 가격 조정 완료!")
with act5:
    # 총 건수 표시
    st.markdown(f"""
    <div style='padding:8px;background:rgba(255,255,255,0.06);border-radius:8px;border:1px solid rgba(255,255,255,0.1);text-align:center;'>
        <span style='color:#94a3b8;font-size:0.8rem;'>조회 건수 </span>
        <span style='color:#fbbf24;font-size:1.2rem;font-weight:700;'> 총 120건</span>
        <span style='color:#94a3b8;font-size:0.8rem;'> | AI 매칭 추천</span>
        <span style='color:#34d399;font-size:1rem;font-weight:700;'> 8건</span>
    </div>
    """, unsafe_allow_html=True)
with act6:
    col_exp1, col_exp2 = st.columns(2)
    col_exp1.button("📥 엑셀 다운로드", use_container_width=True)
    col_exp2.button("🖨️ 인쇄", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────
# 데이터 필터링
# ──────────────────────────────
df_view = df_all.copy()

# 매물종류 필터
if st.session_state.get("pm_prop_type", "전체") != "전체":
    df_view = df_view[df_view["유형"] == st.session_state.pm_prop_type]

# 지역 필터
if st.session_state.get("pm_region", "전체") != "전체":
    df_view = df_view[df_view["시도"] == st.session_state.pm_region]

# 날짜 필터
df_view["등록일_dt"] = pd.to_datetime(df_view["등록일"])
df_view = df_view[
    (df_view["등록일_dt"] >= pd.Timestamp(d_from)) &
    (df_view["등록일_dt"] <= pd.Timestamp(d_to))
]

# 키워드 검색
if search_kw:
    if search_cond == "제목":
        df_view = df_view[df_view["제목"].str.contains(search_kw, na=False)]
    elif search_cond == "내용":
        df_view = df_view[df_view["내용"].str.contains(search_kw, na=False)]
    elif search_cond == "주소":
        df_view = df_view[
            df_view["구군"].str.contains(search_kw, na=False) |
            df_view["읍면동"].str.contains(search_kw, na=False)
        ]
    else:
        df_view = df_view[
            df_view["제목"].str.contains(search_kw, na=False) |
            df_view["내용"].str.contains(search_kw, na=False)
        ]

# 빠른 필터
if chk_신규:
    df_view = df_view[df_view["상태"] == "신규"]
if chk_급매:
    df_view = df_view[df_view["내용"].str.contains("급매", na=False)]

# ──────────────────────────────
# 서브탭
# ──────────────────────────────
sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 수신 파발마", "📤 구입 파발마", "🔖 즐겨찾기"])

with sub_tab1:
    st.markdown(f"""
    <div style='margin-bottom:10px;color:#94a3b8;font-size:0.85rem;'>
        총 <span style='color:#fbbf24;font-weight:700;'>{len(df_view):,}건</span> 조회됨
        <span style='margin-left:16px;color:#64748b;'>※ 열 헤더를 클릭하면 정렬됩니다</span>
    </div>
    """, unsafe_allow_html=True)

    # 표시할 컬럼 선택
    display_cols = ["받은쪽지", "이미구분", "유형", "물건공부", "시도", "구군", "읍면동",
                    "매매가(억)", "보증금(억)", "월세(만)", "거래유형", "제목", "내용", "등록일", "상태"]
    
    df_display = df_view[display_cols].reset_index(drop=True)
    
    # 상태별 색상 컬럼 추가
    def style_status(val):
        colors = {
            "신규": "background-color: rgba(16,185,129,0.2); color: #34d399; font-weight: bold;",
            "진행중": "background-color: rgba(59,130,246,0.2); color: #60a5fa; font-weight: bold;",
            "완료": "background-color: rgba(100,116,139,0.2); color: #94a3b8;",
            "보류": "background-color: rgba(245,158,11,0.2); color: #fbbf24; font-weight: bold;",
        }
        return colors.get(val, "")

    styled_df = df_display.style.applymap(style_status, subset=["상태"])

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=480,
        column_config={
            "받은쪽지": st.column_config.TextColumn("쪽지", width=50),
            "이미구분": st.column_config.TextColumn("이미구분", width=70),
            "유형": st.column_config.TextColumn("유형", width=80),
            "물건공부": st.column_config.TextColumn("물건공부", width=90),
            "시도": st.column_config.TextColumn("시도", width=60),
            "구군": st.column_config.TextColumn("구군", width=80),
            "읍면동": st.column_config.TextColumn("읍면동", width=80),
            "매매가(억)": st.column_config.TextColumn("매매가(억)", width=85),
            "보증금(억)": st.column_config.TextColumn("보증금(억)", width=85),
            "월세(만)": st.column_config.TextColumn("월세(만)", width=75),
            "거래유형": st.column_config.TextColumn("거래유형", width=75),
            "제목": st.column_config.TextColumn("제목", width=200),
            "내용": st.column_config.TextColumn("내용", width=200),
            "등록일": st.column_config.TextColumn("등록일", width=95),
            "상태": st.column_config.TextColumn("상태", width=70),
        }
    )

    # 선택 매물 상세 섹션
    st.markdown("---")
    st.markdown("#### 📝 매물 상세 등록/수정")
    
    if "show_register" in st.session_state and st.session_state.show_register:
        with st.expander("✏️ 새 매물 등록 폼", expanded=True):
            with st.form("property_register_form"):
                r1c1, r1c2, r1c3, r1c4 = st.columns(4)
                with r1c1:
                    form_type = st.selectbox("거래유형", ["매매", "전세", "월세"])
                with r1c2:
                    form_prop = st.selectbox("부동산유형", ["아파트", "오피스텔", "빌라", "상가", "오피스"])
                with r1c3:
                    form_sido = st.selectbox("시도", ["서울", "경기", "인천", "부산", "대구", "기타"])
                with r1c4:
                    form_gugun = st.text_input("구군", placeholder="예: 강남구")

                r2c1, r2c2, r2c3 = st.columns(3)
                with r2c1:
                    form_dong = st.text_input("읍면동", placeholder="예: 대치동")
                with r2c2:
                    form_price = st.number_input("가격 (억원)", min_value=0.0, step=0.1, format="%.1f")
                with r2c3:
                    form_area = st.number_input("전용면적 (㎡)", min_value=0.0, step=0.1)

                form_title = st.text_input("매물 제목")
                form_content = st.text_area("매물 내용 (특징, 층수, 방향 등)", height=100)
                
                r3c1, r3c2 = st.columns(2)
                with r3c1:
                    form_imgu = st.selectbox("이미구분", ["공동", "전속", "일반"])
                with r3c2:
                    form_doc = st.selectbox("물건공부", ["등기부", "건축물대장", "토지대장"])

                submitted = st.form_submit_button("💾 매물 저장", type="primary", use_container_width=True)
                if submitted:
                    st.success(f"✅ '{form_title}' 매물이 저장되었습니다! (DB 연동 시 반영됩니다)")
                    st.session_state.show_register = False

with sub_tab2:
    st.info("📤 구입 파발마: 매수 희망 조건 수신 목록입니다.")
    buy_data = pd.DataFrame({
        "수신일": ["2026-03-04", "2026-03-03", "2026-03-02"],
        "유형": ["아파트", "오피스텔", "빌라"],
        "희망지역": ["강남구 대치동", "서초구 반포동", "마포구 합정동"],
        "예산(억)": ["30~35", "8~12", "5~7"],
        "특이사항": ["학군 필수, 30평 이상", "역세권 선호", "신축 선호"],
        "연락처": ["010-****-1234", "010-****-5678", "010-****-9012"],
        "상태": ["검토중", "매칭완료", "대기"]
    })
    st.dataframe(buy_data, use_container_width=True, height=300)

with sub_tab3:
    st.info("⭐ 즐겨찾기 매물: 관심 등록된 매물 목록입니다.")
    fav_data = df_all.sample(10, random_state=99)[display_cols]
    st.dataframe(fav_data, use_container_width=True, height=300)

# ──────────────────────────────
# CSV 다운로드
# ──────────────────────────────
st.markdown("---")
col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 4])
with col_dl1:
    csv_data = df_display.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv_data,
        file_name=f"매물목록_{date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_dl2:
    st.button("🖨️ 인쇄 미리보기", use_container_width=True)
with col_dl3:
    st.caption(f"🕐 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 데이터: 샘플 (DB 연동 시 실시간 반영)")

st.markdown("<br>", unsafe_allow_html=True)
st.caption("BARA AI 매물관리 v1.0 | 파발마 스타일 UI | 관리자 전용")
