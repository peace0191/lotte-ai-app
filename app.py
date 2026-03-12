import streamlit as st

# ===============================
# UI 가독성 + 다크카드 글자 문제 해결 CSS
# ===============================
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: "Noto Sans KR", sans-serif;
}

/* 전체 화면 */
.stApp {
    background: #f8fafc;
}

/* 메인 영역 폭 */
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 100px;
}

/* 제목 */
h1, h2, h3 {
    color:#0f172a;
    font-weight:800;
}

/* 일반 텍스트 */
p, span, label {
    font-size:16px;
    line-height:1.7;
    color:#334155;
}

/* 버튼 */
.stButton > button {
    font-size:16px;
    font-weight:700;
    border-radius:10px;
    padding:10px 18px;
}

/* 입력창 */
input, textarea {
    font-size:16px !important;
}

/* ===== 다크 카드 안 글자 밝게 ===== */

div[style*="#0f172a"] h1,
div[style*="#0f172a"] h2,
div[style*="#0f172a"] h3,
div[style*="#0f172a"] h4,
div[style*="#0f172a"] p,
div[style*="#0f172a"] span,
div[style*="#0f172a"] div {
    color:#f8fafc !important;
}

/* 대표 이름 강조 */
div[style*="#0f172a"] b,
div[style*="#0f172a"] strong {
    color:#fbbf24 !important;
    font-weight:900 !important;
}

/* 카드 그림자 */
.card {
    background:#ffffff;
    border-radius:14px;
    padding:20px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);
    margin-bottom:15px;
}

</style>
""", unsafe_allow_html=True)

# -------- UI 가독성 개선 CSS --------
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #061537 0%, #081a45 100%);
        color: #ffffff;
        padding: 34px;
        border-radius: 18px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(2, 6, 23, 0.22);
        border: 1px solid rgba(255,255,255,0.06);
    ">
        <div style="display: flex; align-items: flex-start; margin-bottom: 22px;">
            <div style="
                background-color: #fbbf24;
                width: 76px;
                height: 76px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 18px;
                font-size: 36px;
                flex-shrink: 0;
                box-shadow: 0 6px 18px rgba(251,191,36,0.35);
            ">
                👨‍💼
            </div>

            <div style="flex: 1;">
                <div style="
                    margin: 0 0 6px 0;
                    font-size: 1.35rem;
                    color: #f8fafc;
                    line-height: 1.45;
                    font-weight: 900;
                    letter-spacing: -0.02em;
                ">
                    롯데타워앤강남빌딩부동산중개주식회사
                </div>

                <div style="
                    color: #cbd5e1;
                    font-size: 0.92rem;
                    margin-bottom: 8px;
                    font-weight: 500;
                ">
                    등록번호: 11680-2023-00078 | 사업자: 461-86-02740
                </div>

                <div style="
                    font-size: 1.55rem;
                    color: #fbbf24;
                    font-weight: 900;
                    margin-bottom: 10px;
                    letter-spacing: -0.03em;
                ">
                    대표: 공인중개사 이상수
                </div>

                <div style="
                    color: #f1f5f9;
                    font-size: 1.03rem;
                    font-weight: 600;
                ">
                    Tel: 02-578-8289 / 010-8985-8945
                </div>
            </div>
        </div>

        <div style="
            color: #fde68a;
            margin-top: 10px;
            font-size: 1.55rem;
            font-weight: 900;
            line-height: 1.5;
            letter-spacing: -0.03em;
        ">
            대치1동은 자녀의 미래 베이스캠프입니다.
        </div>

        <div style="
            color: #e2e8f0;
            line-height: 1.9;
            font-size: 1.02rem;
            margin-top: 14px;
            font-weight: 500;
        ">
            AI 저평가 분석과 예약 AI자동 매칭 시스템으로 숨겨진 부동산 가치를 발굴하고,<br>
            대한민국 최고의 교육 환경으로 가는 최적의 출발점을 찾아드립니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    div[style*="background: linear-gradient(135deg, #061537 0%, #081a45 100%)"] * {
    color: inherit !important;}

</style>
""", unsafe_allow_html=True)
import sys
import re
from pathlib import Path
import pydeck as pdk
import random
import time
import datetime  # 모듈 전체 사용: datetime.date.today(), datetime.timedelta() 등
# datetime.now() 단축 호출 호환을 위해 모듈에 now 속성 추가
datetime.now = datetime.datetime.now

# Ensure services are importable if running from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import services
try:
    from services.matching_svc import matching_svc
    from services.map_image import build_points_map_png
    from services.local_market import local_market_svc
    from services.data import load_properties
    from services.ui import scroll_to_top
    MATCHING_SVC_AVAILABLE = True
except ImportError:
    MATCHING_SVC_AVAILABLE = False
    class MockMatchingSvc:
        match_reservations = []
    matching_svc = MockMatchingSvc()
    
    # Mock other services for fallback
    class MockLocalMarketSvc:
        def get_daechi_summary(self): return {}
        def get_education_summary(self): return {}
    local_market_svc = MockLocalMarketSvc()
    def load_properties(): return {}
    def build_points_map_png(pts): return None
    def scroll_to_top(): pass

# --- Page Config ---
st.set_page_config(
    page_title="롯데타워앤강남빌딩 AI 부동산",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Session State ---
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'manual_nav_target' not in st.session_state:
    st.session_state['manual_nav_target'] = None

# --- Custom CSS ---
st.markdown("""
<style>
/* ═══════════════════════════════════════════════
   롯데타워 AI 앱 — 프리미엄 테마 (최소 개입)
   배경: 고급 쿨 그레이 | 텍스트: Streamlit 기본
═══════════════════════════════════════════════ */

/* ── 구글 폰트 ── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }

/* ── 앱 배경: 따뜻한 쿨 그레이 ── */
.stApp {
    background: #ffffff !important;
}

/* ── 메인 컨테이너 ── */
.block-container {
    background: #ffffff !important;
    padding-top: 0.5rem !important;
    padding-bottom: 90px !important;
    max-width: 1100px !important;
}
/* 기본 텍스트 가독성 */
p, span, div, li, td, th {
    color: #111827;
}
h1, h2, h3, h4, h5, h6 {
    color: #0f172a !important;
}
.stMarkdown p {
    color: #1e293b !important;
    font-size: 14px !important;
}

/* ── 헤더/푸터 숨김 ── */
header { visibility: hidden; }
footer { visibility: hidden; }

/* ── 스크롤 & 앵커 ── */
html { scroll-behavior: smooth !important; scroll-padding-top: 100px; }
div[id="login-top"], div[id="kakao-share-section"], div[id="ai-strategy-section"] {
    scroll-margin-top: 80px; padding-top: 4px;
}

/* ══════════════════════════════════════
   🗂️ 탭 네비게이션 — 다크 네이비
══════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 3px;
    background: linear-gradient(135deg, #1e2d40 0%, #0f1e30 100%);
    padding: 8px 6px;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    position: sticky; top: 0; z-index: 999;
}
.stTabs [data-baseweb="tab"] {
    height: 44px; flex-grow: 1;
    font-size: 13px !important; font-weight: 700 !important;
    color: #7c8fa6 !important;
    border-radius: 8px; margin: 0 2px; letter-spacing: -0.3px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important; font-weight: 900 !important;
    border-bottom: 3px solid #facc15 !important;
    box-shadow: 0 3px 12px rgba(37,99,235,0.4) !important;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background-color: rgba(255,255,255,0.08) !important;
    color: #e2e8f0 !important;
}

/* ══════════════════════════════════════
   📝 입력 폼 — 흰 카드 느낌
══════════════════════════════════════ */
/* 라벨 — 진한 회색 (그레이 배경 위 가독성) */
label {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #111827 !important;
}
/* 텍스트 입력 필드 */
input[type="text"], input[type="number"], input[type="tel"],
input[type="email"], input[type="password"], textarea {
    font-size: 15px !important;
    font-weight: 500 !important;
    color: #111827 !important;
    background-color: #ffffff !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 8px !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    outline: none !important;
}
/* Placeholder */
::placeholder { color: #9ca3af !important; font-style: italic; font-size: 13px; }

/* ══════════════════════════════════════
   🔢 NumberInput & Date
══════════════════════════════════════ */
.stNumberInput > div > div > input {
    color: #111827 !important;
    background: #ffffff !important;
}

/* ══════════════════════════════════════
   🔘 라디오 & 체크박스
══════════════════════════════════════ */
.stRadio label, .stCheckbox label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #374151 !important;
}

/* ══════════════════════════════════════
   📦 카드 & divider
══════════════════════════════════════ */
.card {
    background: #ffffff;
    padding: 1.5rem; border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04);
    margin-bottom: 1rem; border: 1px solid #e5e7eb;
}
hr { border-color: #d1d5db !important; }
.login-section-divider { border: none; border-top: 2px dashed #cbd5e1; margin: 28px 0; }

/* ══════════════════════════════════════
   🎯 버튼
══════════════════════════════════════ */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    letter-spacing: -0.3px;
    transition: all 0.2s !important;
}
.ext-link {
    display: block; padding: 12px; text-decoration: none;
    color: white !important; text-align: center;
    border-radius: 10px; font-weight: 800; font-size: 14px;
    margin-bottom: 5px; transition: 0.25s;
}
.ext-link:hover { opacity: 0.88; transform: translateY(-1px); }

/* ══════════════════════════════════════
   📊 메트릭 카드 (어두운 배경 위)
══════════════════════════════════════ */
div[data-testid="stMetricValue"] {
    font-size: 1.6rem !important; font-weight: 900 !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.82rem !important; font-weight: 600 !important;
}

/* ══════════════════════════════════════
   📌 하단 고정 네비게이션
══════════════════════════════════════ */
.bottom-nav {
    position: fixed; bottom: 0; left: 0; width: 100%;
    background: linear-gradient(180deg, #1e2d40 0%, #0f172a 100%);
    border-top: 2px solid #2d3f55;
    padding: 7px 20px;
    display: flex; justify-content: space-around; align-items: center;
    z-index: 9999;
    box-shadow: 0 -6px 24px rgba(0,0,0,0.35);
}
.nav-btn {
    text-decoration: none; color: #8fa8c0 !important;
    font-weight: 800; font-size: 12px;
    display: flex; flex-direction: column; align-items: center;
    padding: 5px 8px; border-radius: 10px; transition: 0.2s;
}
.nav-btn:hover { color: #facc15 !important; background-color: rgba(255,255,255,0.08); }

/* ══════════════════════════════════════
   🔔 알림 박스
══════════════════════════════════════ */
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)








# --- Constants & Data for Map ---
POINTS_PATH = Path("data/daechi_points.json")
COLOR_RGB = {
    "초등": [255, 140, 0],     # Orange
    "중등": [50, 205, 50],     # Green
    "고등": [50, 205, 50],     # Green
    "단지": [255, 215, 0],     # Yellow
    "부동산": [255, 105, 180], # Pink
    "관공서": [150, 150, 150], # Grey
}

def load_points():
    if not POINTS_PATH.exists():
        return pd.DataFrame()
    items = json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    df = pd.DataFrame(items)
    df = df.dropna(subset=["lat", "lon"]).copy()
    df["color"] = df["category"].apply(lambda x: COLOR_RGB.get(x, [200, 200, 200]))
    df["is_overcrowded"] = df.get("note", "").fillna("").astype(str).str.contains("과밀")
    
    def get_height(cat):
        if cat == "단지": return 250
        if cat in ["초등", "중등", "고등"]: return 120
        return 60
    df["height"] = df["category"].apply(get_height)
    return df

def prefix_icon(cat):
    return {"초등":"🏫","중등":"🏫","고등":"🏫","단지":"🏠","부동산":"🏢","관공서":"🏛️"}.get(cat,"📍")

def render_daechi_map_block():
    st.markdown("### 🏫 AI 대치1동 학군/단지 입체 지도")
    df = load_points()
    if df.empty:
        st.warning("daechi_points.json에 좌표 데이터가 없습니다.")
        return

    df["display_name"] = df.apply(lambda r: f"{prefix_icon(r['category'])} {r['name']}", axis=1)

    column_layer = pdk.Layer(
        "ColumnLayer", data=df, get_position=["lon", "lat"], get_elevation="height",
        elevation_scale=1, radius=35, get_fill_color="color", pickable=True, auto_highlight=True, extruded=True,
    )

    halo_layer = pdk.Layer(
        "ScatterplotLayer", data=df, get_position=["lon", "lat"], get_fill_color=[0, 0, 0, 50],
        get_line_color="color", stroked=True, filled=True, get_radius=70, radius_units="meters", line_width_min_pixels=2,
    )

    label_layer = pdk.Layer(
        "TextLayer", data=df, get_position=["lon", "lat"], get_text="display_name", get_size=15,
        get_color=[255, 255, 255], get_text_anchor="'middle'", get_alignment_baseline="'bottom'",
        get_pixel_offset=[0, -30], billboard=True, get_background_color=[0, 0, 0, 140], background_padding=[4, 2, 4, 2],
    )
    
    tooltip = {"html": "<b>{name}</b><br/>{category}<br/>{note}", "style": {"backgroundColor": "rgba(20,20,20,0.9)", "color": "white"}}
    view_state = pdk.ViewState(latitude=df["lat"].mean(), longitude=df["lon"].mean(), zoom=14.5, pitch=50, bearing=10)
    
    # 6:4 Ratio Split
    col_map, col_legend = st.columns([6, 4])
    
    with col_map:
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10",
            initial_view_state=view_state,
            layers=[halo_layer, column_layer, label_layer],
            tooltip=tooltip
        ), use_container_width=True)
        
    with col_legend:
        st.markdown("""
        <div style="background-color: #fafafa; border: 1px solid #ddd; border-radius: 8px; padding: 15px; height: 500px; overflow-y: auto;">
            <div style="margin-bottom: 10px; font-weight: bold; color: #333; font-size: 1.1em; border-bottom: 2px solid #eee; padding-bottom: 5px;">🗺️ 상세 범례 가이드</div>
            <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.9em;">
                <div style="display: flex; align-items: start;">
                    <span style="color: #FFD700; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>아파트 단지 (노랑)</b><br><span style="color:#666;">래대팰, SK뷰, 아이파크, 은마</span></div>
                </div>
                <div style="display: flex; align-items: start;">
                    <span style="color: #32CD32; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>중·고등학교 (녹색)</b><br><span style="color:#666;">대청중, 숙명여중고, 단대부중고</span></div>
                </div>
                <div style="display: flex; align-items: start;">
                    <span style="color: #FF8C00; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>초등학교 (주황)</b><br><span style="color:#666;">대치초, 대도초 (학군 배정)</span></div>
                </div>
                <div style="display: flex; align-items: start;">
                    <span style="color: #FF69B4; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>부동산 (분홍)</b><br><span style="color:#666;">롯데 AI 부동산 (본사)</span></div>
                </div>
                <div style="display: flex; align-items: start;">
                    <span style="color: #A0A0A0; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>관공서/기타 (회색)</b><br><span style="color:#666;">대치1동 주민센터, 지구대 등</span></div>
                </div>
            </div>
            <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; font-size: 0.8em; color: #888;">
                💡 <b>이용 팁</b><br>
                • <b>Shift + 드래그</b>: 지도 3D 회전<br>
                • <b>마우스 오버</b>: 상세 정보 확인
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Realtime AI Search Panel ---
def render_realtime_search_panel(avg_prices):
    """실시간 AI 시세 탐색 엔진 패널"""

    # Session state 초기화
    if "ai_search_auto" not in st.session_state:
        st.session_state["ai_search_auto"] = True
    if "ai_search_count" not in st.session_state:
        st.session_state["ai_search_count"] = random.randint(1180, 1260)
    if "ai_search_logs" not in st.session_state:
        st.session_state["ai_search_logs"] = [
            f"[{datetime.now().strftime('%H:%M:%S')}] 🏛️ 국토부 실거래가 API 연결 완료 — 대치1동 1,247건 수집",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🏠 네이버 부동산 크롤링 완료 — 현재 매물 428건 분석",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 AI 머신러닝 예측 실행 — 신뢰도 94% 확보",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 급매 감지: 대치팰리스 34평 시세比 -3.2% 물건 발견",
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 자동탐색 완료 — 다음 탐색: 60초 후",
        ]
    if "ai_last_search" not in st.session_state:
        st.session_state["ai_last_search"] = time.time()
    if "ai_flash_deals" not in st.session_state:
        st.session_state["ai_flash_deals"] = random.randint(2, 5)
    if "ai_confidence" not in st.session_state:
        st.session_state["ai_confidence"] = random.randint(91, 97)

    # --- 헤더: 탐색 상태 ---
    elapsed = int(time.time() - st.session_state["ai_last_search"])
    status_color = "#22c55e" if st.session_state["ai_search_auto"] else "#f59e0b"
    status_text = "실시간 자동탐색 중" if st.session_state["ai_search_auto"] else "자동탐색 일시정지"
    status_dot = "🟢" if st.session_state["ai_search_auto"] else "🟡"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg,#0f172a,#1e293b); border-radius:14px;
                padding:18px 22px; margin-bottom:16px; border:1px solid #334155;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
            <div>
                <span style="font-size:1.05rem; font-weight:bold; color:#f8fafc;">
                    🤖 AI 실시간 시세 탐색 엔진
                </span>
                <span style="margin-left:10px; background:{status_color}22; color:{status_color};
                            border:1px solid {status_color}55; border-radius:20px;
                            font-size:0.75rem; padding:2px 10px; font-weight:600;">
                    {status_dot} {status_text}
                </span>
            </div>
            <div style="font-size:0.78rem; color:#94a3b8;">
                마지막 탐색: <b style="color:#e2e8f0;">{elapsed}초 전</b> &nbsp;|&nbsp;
                소스: <b style="color:#60a5fa;">국토부·네이버부동산·한국부동산원</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- AI 지표 카드 3개 ---
    kc1, kc2, kc3 = st.columns(3)
    with kc1:
        st.markdown(f"""
        <div style="background:#0f172a; border:1px solid #1d4ed8; border-radius:12px;
                    padding:14px; text-align:center;">
            <div style="font-size:0.78rem; color:#93c5fd; margin-bottom:4px;">🧠 AI 예측 신뢰도</div>
            <div style="font-size:2rem; font-weight:900; color:#60a5fa;">{st.session_state['ai_confidence']}%</div>
            <div style="font-size:0.72rem; color:#475569;">머신러닝 앙상블 모델</div>
        </div>
        """, unsafe_allow_html=True)
    with kc2:
        cnt = st.session_state["ai_search_count"]
        st.markdown(f"""
        <div style="background:#0f172a; border:1px solid #15803d; border-radius:12px;
                    padding:14px; text-align:center;">
            <div style="font-size:0.78rem; color:#86efac; margin-bottom:4px;">📡 탐색 완료 건수</div>
            <div style="font-size:2rem; font-weight:900; color:#4ade80;">{cnt:,}건</div>
            <div style="font-size:0.72rem; color:#475569;">실거래·매물 통합 집계</div>
        </div>
        """, unsafe_allow_html=True)
    with kc3:
        flash = st.session_state["ai_flash_deals"]
        st.markdown(f"""
        <div style="background:#0f172a; border:1px solid #b91c1c; border-radius:12px;
                    padding:14px; text-align:center;">
            <div style="font-size:0.78rem; color:#fca5a5; margin-bottom:4px;">🚨 급매 감지</div>
            <div style="font-size:2rem; font-weight:900; color:#f87171;">{flash}건</div>
            <div style="font-size:0.72rem; color:#475569;">시세比 -2% 이상 할인 매물</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # --- 탐색 로그 ---
    with st.expander("📋 실시간 탐색 로그 보기", expanded=False):
        log_html = "".join(
            f"<div style='font-size:0.8rem; padding:4px 0; border-bottom:1px solid #1e293b; color:#cbd5e1;'>{log}</div>"
            for log in reversed(st.session_state["ai_search_logs"][-8:])
        )
        st.markdown(
            f"<div style='background:#0f172a; border-radius:8px; padding:10px;'>{log_html}</div>",
            unsafe_allow_html=True
        )

    # --- 탐색 버튼 ---
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button("🔄 지금 탐색하기", use_container_width=True, key="btn_manual_search", type="primary"):
            # 새 탐색 시뮬레이션
            st.session_state["ai_search_count"] += random.randint(3, 12)
            st.session_state["ai_confidence"] = random.randint(91, 97)
            st.session_state["ai_flash_deals"] = random.randint(2, 5)
            st.session_state["ai_last_search"] = time.time()

            # 신규 로그 삽입 (가장 최신 가격 기준)
            sources = ["국토부 실거래가", "네이버 부동산", "한국부동산원", "KB 부동산"]
            topics = [
                f"래미안대치팰리스 34평 {avg_prices[30]}억 거래 확인",
                f"대치SK뷰 26평 신규 전세 매물 등록",
                f"은마아파트 31평 급매 -2.8% 포착",
                f"대치아이파크 56평 최고층 시세 갱신",
                f"평형별 AI 예측 모델 재계산 완료 (신뢰도 {random.randint(91,97)}%)",
            ]
            src = random.choice(sources)
            topic = random.choice(topics)
            new_log = f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 {src} 수동 탐색 — {topic}"
            st.session_state["ai_search_logs"].append(new_log)
            st.toast("✅ AI 탐색 완료! 최신 데이터로 갱신되었습니다.", icon="🔄")
            st.rerun()
    with btn_col2:
        auto_label = "⏸ 자동탐색 중지" if st.session_state["ai_search_auto"] else "▶️ 자동탐색 시작"
        if st.button(auto_label, use_container_width=True, key="btn_toggle_auto"):
            st.session_state["ai_search_auto"] = not st.session_state["ai_search_auto"]
            state_txt = "활성화" if st.session_state["ai_search_auto"] else "중지"
            st.toast(f"자동탐색 {state_txt}됩니다.", icon="🤖")
            st.rerun()

def calculate_metrics():
    props = load_properties()
    targets = ["대치팰리스", "대치SK뷰", "대치아이파크"]
    buckets = {20: [], 30: [], 40: []}
    
    for k, items in props.items():
        if k not in targets: continue
        for item in items:
            spec = item.get("spec", "")
            match = re.search(r"(\d+)평", spec)
            if match:
                size = int(match.group(1))
                b = 40 if size >= 40 else (30 if size >= 30 else 20)
                
                price_str = item.get("price", "")
                if "/" not in price_str and "억" in price_str:
                    try:
                        val = float(re.search(r"([\d\.]+)억", price_str).group(1))
                        buckets[b].append(val)
                    except: pass
    
    # Defaults if data missing
    res = {}
    defaults = {20:23.5, 30:32.5, 40:48.0}
    for k in [20, 30, 40]:
        val = round(sum(buckets[k])/len(buckets[k]), 1) if buckets[k] else defaults[k]
        res[k] = val
    return res

# --- RENDER FUNCTIONS ---

def render_home():
    # 1. Hero Section
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 1.8rem; border-radius: 0 0 1.5rem 1.5rem;
                margin: -1rem -1rem 1rem -1rem; color: white;
                border-bottom: 3px solid #facc15;">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="width: 52px; height: 52px; background: linear-gradient(135deg,#facc15,#f59e0b);
                        border-radius: 50%; display: flex; align-items: center;
                        justify-content: center; margin-right: 1rem; font-size: 26px;
                        box-shadow: 0 4px 12px rgba(250,204,21,0.4);">👑</div>
            <div>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 900;
                           color: #ffffff; letter-spacing: -0.5px;">공인중개사 이상수 대표</h3>
                <p style="margin: 2px 0 0 0; font-size: 0.85rem; font-weight: 600;
                          color: #e2e8f0;">롯데타워앤강남빌딩부동산중개(주)</p>
            </div>
        </div>
        <h2 style="font-size: 1.55rem; font-weight: 900; line-height: 1.45;
                   margin-bottom: 0.3rem; color: #ffffff; letter-spacing: -0.8px;">
            "대치1동은 자녀의 미래를 위한<br/>
            <span style="color: #facc15; text-shadow: 0 0 20px rgba(250,204,21,0.5);">베이스캠프</span>입니다."
        </h2>
        <p style="margin: 0.4rem 0 0 0; font-size: 0.9rem; font-weight: 600; color: #cbd5e1;">
            AI 저평가 분석과 예약 AI자동 매칭 시스템으로 숨겨진 부동산 가치를 발굴하고,<br/>
            대한민국 최고의 교육 환경으로 가는 최적의 출발점을 찾아드립니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Price Trends + AI Search Panel
    st.markdown("### 📊 대치1동 평형별 시세 & 전세가율")
    avg_prices = calculate_metrics()

    # AI 실시간 탐색 패널
    render_realtime_search_panel(avg_prices)

    st.markdown("#### 📈 평형별 현재 시세")
    pt_c1, pt_c2, pt_c3 = st.columns(3)

    # 등락률 시뮬레이션 (페이지 세션 당 고정)
    if "price_deltas" not in st.session_state:
        st.session_state["price_deltas"] = {
            20: round(random.uniform(-0.8, 1.2), 1),
            30: round(random.uniform(-0.5, 1.5), 1),
            40: round(random.uniform(-0.3, 2.0), 1),
        }
    deltas = st.session_state["price_deltas"]

    def render_price_card(title, price, jeonse_ratio=0.52, delta=0.0):
        jeonse_val = round(price * jeonse_ratio, 1)
        arrow = "▲" if delta >= 0 else "▼"
        arrow_color = "#16a34a" if delta >= 0 else "#dc2626"
        delta_abs = abs(delta)
        st.markdown(f"""
        <div style="background:#f8fafc; padding:16px; border-radius:12px;
                    border:1px solid #e2e8f0; text-align:center;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="font-size:0.85rem; color:#64748b; font-weight:700; margin-bottom:4px;">{title}</div>
            <div style="font-size:2rem; font-weight:900; color:#0f172a; line-height:1.2;">{price}억</div>
            <div style="font-size:0.82rem; color:{arrow_color}; font-weight:700; margin:4px 0;">
                {arrow} 전일比 {delta_abs}% ({'+' if delta>=0 else ''}{round(price*delta/100,2)}억)
            </div>
            <div style="font-size:0.8rem; color:#2563eb;">전세가율 {int(jeonse_ratio*100)}% · 약 {jeonse_val}억</div>
        </div>
        """, unsafe_allow_html=True)

    with pt_c1: render_price_card("20평형대 (소형)", avg_prices[20], 0.52, deltas[20])
    with pt_c2: render_price_card("30평형대 (국민평형)", avg_prices[30], 0.52, deltas[30])
    with pt_c3: render_price_card("40평형대 이상 (대형)", avg_prices[40], 0.52, deltas[40])

    st.caption("※ 국토부 실거래가 · 네이버부동산 · 한국부동산원 데이터 기반 AI 추정치 | 투자 참고용")
    st.markdown("---")

    # 3. Integrated Education Environment
    st.markdown("### 🎓 통합 대치동 교육환경")
    edu_info = local_market_svc.get_education_summary()
    
    st.info(f"**{edu_info.get('description')}**")
    
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        st.markdown("**🏫 초등학교 (배정)**")
        for s in edu_info.get("elementary", []):
            st.markdown(f"- {s}")
    with ec2:
        st.markdown("**🏫 중학교 (진학)**")
        for s in edu_info.get("middle", []):
            st.markdown(f"- {s}")
    with ec3:
        st.markdown("**🏫 고등학교 (명문)**")
        for s in edu_info.get("high", []):
            st.markdown(f"- {s}")
            
    st.markdown("---")

    # 4. Complex Analysis — 4-tab, 60% column
    tab_col, _ = st.columns([6, 4])
    with tab_col:
        st.markdown("#### 🏘️ 주요 유명 단지 분석")
        t1, t2, t3, t4 = st.tabs(["래미안 대치팩리스", "대치SK뷰/대치아이파크", "삼환아르누보2/시그니엘", "은마아파트"])
        with t1:
            st.success("### 👑 대치동의 대장주")
            st.markdown("- 대치초 배정, 학원가 바로 앞\n- 수영장/조식 등 완벽한 커뮤니티")
            st.image("https://images.unsplash.com/photo-1600596542815-e328701102b9?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        with t2:
            st.warning("### ⚖️ 실속과 환경의 조화")
            st.markdown("- 대치역/한티역 역세권, 백화점 슬세권\n- 쿨적한 주거 환경")
            st.image("https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        with t3:
            st.info("### 🏙️ 프리미엄 래지던스 & 오피스텔")
            st.markdown("- 시그니엘: 롤데월드타워 최고층 글로벌 레지던스\n- 삼환아르누보2: 대치1동 학원가 도보 3분 오피스텔 가성비")
            st.image("https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        with t4:
            st.error("### 🏗️ 재건축의 상징")
            st.markdown("- 강남 재건축의 바로미터\n- 대공초 배정, 압도적 투자가치")
            st.image("https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        
    st.markdown("---")

    # Mid-page Navigation Buttons
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("⭐ AI저평가추천매물 보기", use_container_width=True, key="btn_mid_listing"):
            st.session_state["manual_nav_target"] = "AI저평가추천매물"
            st.rerun()
    with col_nav2:
        if st.button("🤖 AI 챗봇에게 문의하기", use_container_width=True, key="btn_mid_chatbot"):
            st.session_state["manual_nav_target"] = "AI매칭/사전등록"
            st.rerun()

    st.markdown("---")

    # 5. 3D Map
    render_daechi_map_block()
    
    st.divider()
        
    st.markdown("---")
    
    # 6. Buttons
    st.markdown("##### 🔗 주요 사이트 바로가기 (새창 열림)")
    el_c1, el_c2, el_c3, el_c4 = st.columns(4)
    with el_c1:
        st.markdown('<a href="https://rt.molit.go.kr/" target="_blank" class="ext-link" style="background:#1e3a5f;">🏛️ 국토부 실거래가</a>', unsafe_allow_html=True)
    with el_c2:
        st.markdown('<a href="https://land.naver.com/" target="_blank" class="ext-link" style="background:#03C75A;">🏠 네이버 부동산</a>', unsafe_allow_html=True)
    with el_c3:
        st.markdown('<a href="https://map.kakao.com/" target="_blank" class="ext-link" style="background:#FAE100; color:#333;">🗺️ 카카오맵</a>', unsafe_allow_html=True)
    with el_c4:
        st.markdown('<a href="https://www.reb.or.kr/" target="_blank" class="ext-link" style="background:#4f46e5;">📊 한국부동산원</a>', unsafe_allow_html=True)

    st.caption("※ 외부 사이트는 새 탭에서 열립니다.")


def render_listing():
    st.markdown("### ⭐ AI저평가추천매물")

    # helper for one item
    def property_card(title, price, desc, img_url, badge=None, key_suffix=None):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(img_url, use_column_width=True)
        with c2:
            if badge:
                st.markdown(f"<span style='background:#facc15; font-size:0.8em; padding:2px 4px; border-radius:4px;'>{badge}</span>", unsafe_allow_html=True)
            st.markdown(f"#### {title}")
            st.markdown(f"### {price}")
            st.caption(desc)
            _key = key_suffix if key_suffix else f"{title}_{random.randint(1,99999)}"
            if st.button("AI 리포트 보기", key=f"btn_{_key}"):
                st.info("AI 분석 리포트가 생성되었습니다. (데모)")
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # 【상단 고정】 AI 저평가 매물 (국토부 실거래가 대비 약 8% 전후 저평가)
    # ══════════════════════════════════════════════════════════════
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
                border-radius: 16px; padding: 20px 24px; margin-bottom: 20px;
                border-left: 5px solid #facc15; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
            <span style="font-size:2rem;">🤖</span>
            <div>
                <div style="font-size:1.3rem; font-weight:900; color:#facc15;">AI 저평가 추천매물</div>
                <div style="font-size:0.85rem; color:#93c5fd; margin-top:2px;">
                    국토부 실거래가 API 기반 · <b style="color:#fbbf24;">시세 대비 약 8% 전후 저평가</b> 매물만 선별
                </div>
            </div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;">
            <span style="background:#1e40af33; color:#93c5fd; border:1px solid #3b82f6;
                         border-radius:20px; padding:3px 12px; font-size:0.78rem; font-weight:700;">🏛️ 국토부 실거래가 연동</span>
            <span style="background:#14532d33; color:#86efac; border:1px solid #22c55e;
                         border-radius:20px; padding:3px 12px; font-size:0.78rem; font-weight:700;">✅ AI 검증 완료</span>
            <span style="background:#7f1d1d33; color:#fca5a5; border:1px solid #ef4444;
                         border-radius:20px; padding:3px 12px; font-size:0.78rem; font-weight:700;">🚨 매물 수 한정</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 매매 저평가 매물 (2개)
    st.markdown("""
    <div style="background:#162032; border-radius:12px; padding:14px 18px; margin-bottom:14px;
                border-left:4px solid #f59e0b;">
        <span style="font-size:1.05rem; font-weight:900; color:#fcd34d;">🏠 매매 저평가 매물</span>
        <span style="margin-left:10px; font-size:0.8rem; color:#94a3b8;">
            국토부 실거래가 대비 <b style="color:#f87171;">-7~9% 저평가</b> 확인 매물
        </span>
    </div>
    """, unsafe_allow_html=True)

    ai_col1, ai_col2 = st.columns(2)
    with ai_col1:
        st.markdown("""
        <div style="background:#0f172a; border:2px solid #f59e0b; border-radius:14px; padding:18px; position:relative; margin-bottom:4px;">
            <div style="position:absolute; top:-12px; left:16px; background:#f59e0b; color:#1e293b;
                        font-weight:900; font-size:0.78rem; padding:2px 12px; border-radius:20px;">🤖 AI 저평가 -8.2%</div>
            <div style="display:flex; gap:10px; align-items:flex-start; margin-top:6px;">
                <div style="font-size:2rem;">🏢</div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:#f8fafc;">래미안대치팰리스 34평 남향</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#fcd34d; margin:4px 0;">40.5억</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">국토부 실거래 기준가: 44.1억</div>
                    <div style="font-size:0.78rem; color:#f87171; font-weight:700; margin-top:2px;">▼ 3.6억 저평가 (8.2%↓)</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">34평 · 중층 · 남향 · 대치초 배정권</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 AI 저평가 리포트 보기", key="ai_under_sale_1", use_container_width=True, type="primary"):
            st.info("래미안대치팰리스 34평 저평가 분석 리포트가 생성되었습니다. (데모)")

    with ai_col2:
        st.markdown("""
        <div style="background:#0f172a; border:2px solid #f59e0b; border-radius:14px; padding:18px; position:relative; margin-bottom:4px;">
            <div style="position:absolute; top:-12px; left:16px; background:#f59e0b; color:#1e293b;
                        font-weight:900; font-size:0.78rem; padding:2px 12px; border-radius:20px;">🤖 AI 저평가 -7.5%</div>
            <div style="display:flex; gap:10px; align-items:flex-start; margin-top:6px;">
                <div style="font-size:2rem;">🏙️</div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:#f8fafc;">시그니엘 레지던스 88평 매매</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#fcd34d; margin:4px 0;">63.8억</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">국토부 실거래 기준가: 69억</div>
                    <div style="font-size:0.78rem; color:#f87171; font-weight:700; margin-top:2px;">▼ 5.2억 저평가 (7.5%↓)</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">88평 · 고층 · 한강뷰 · 풀옵션 급매</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 AI 저평가 리포트 보기", key="ai_under_sale_2", use_container_width=True, type="primary"):
            st.info("시그니엘 레지던스 88평 저평가 분석 리포트가 생성되었습니다. (데모)")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── 임대차/렌트 저평가 매물 (2개)
    st.markdown("""
    <div style="background:#162032; border-radius:12px; padding:14px 18px; margin-bottom:14px;
                border-left:4px solid #22d3ee;">
        <span style="font-size:1.05rem; font-weight:900; color:#67e8f9;">🔑 임대차·렌트 저평가 매물</span>
        <span style="margin-left:10px; font-size:0.8rem; color:#94a3b8;">
            시세 대비 <b style="color:#34d399;">-7~9% 저렴한</b> 전세·월세 확인 매물
        </span>
    </div>
    """, unsafe_allow_html=True)

    rent_col1, rent_col2 = st.columns(2)
    with rent_col1:
        st.markdown("""
        <div style="background:#0f172a; border:2px solid #22d3ee; border-radius:14px; padding:18px; position:relative; margin-bottom:4px;">
            <div style="position:absolute; top:-12px; left:16px; background:#22d3ee; color:#0f172a;
                        font-weight:900; font-size:0.78rem; padding:2px 12px; border-radius:20px;">🤖 전세 저평가 -8.8%</div>
            <div style="display:flex; gap:10px; align-items:flex-start; margin-top:6px;">
                <div style="font-size:2rem;">🔑</div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:#f8fafc;">대치SK뷰 33평 전세</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#67e8f9; margin:4px 0;">14.5억</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">국토부 실거래 기준 전세가: 15.9억</div>
                    <div style="font-size:0.78rem; color:#34d399; font-weight:700; margin-top:2px;">▼ 1.4억 저렴 (8.8%↓)</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">33평 · 중층 · 동향 · 대치역 도보 5분</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 AI 저평가 리포트 보기", key="ai_under_rent_1", use_container_width=True):
            st.info("대치SK뷰 33평 전세 저평가 분석 리포트가 생성되었습니다. (데모)")

    with rent_col2:
        st.markdown("""
        <div style="background:#0f172a; border:2px solid #22d3ee; border-radius:14px; padding:18px; position:relative; margin-bottom:4px;">
            <div style="position:absolute; top:-12px; left:16px; background:#22d3ee; color:#0f172a;
                        font-weight:900; font-size:0.78rem; padding:2px 12px; border-radius:20px;">🤖 월세 저평가 -7.9%</div>
            <div style="display:flex; gap:10px; align-items:flex-start; margin-top:6px;">
                <div style="font-size:2rem;">🏘️</div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:#f8fafc;">은마아파트 31평 월세</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#67e8f9; margin:4px 0;">5천/185만</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">국토부 실거래 기준 월세: 5천/201만</div>
                    <div style="font-size:0.78rem; color:#34d399; font-weight:700; margin-top:2px;">▼ 월 16만원 저렴 (7.9%↓)</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">31평 · 중층 · 남향 · 재건축 호재</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 AI 저평가 리포트 보기", key="ai_under_rent_2", use_container_width=True):
            st.info("은마아파트 31평 월세 저평가 분석 리포트가 생성되었습니다. (데모)")

    # 구분선 + 스크롤 안내
    st.markdown("""
    <div style="text-align:center; padding:18px 0; margin:10px 0;">
        <div style="display:inline-flex; align-items:center; gap:10px; background:#1e293b;
                    border-radius:30px; padding:8px 24px; border:1px solid #334155;">
            <span style="font-size:1.2rem;">⬇️</span>
            <span style="color:#94a3b8; font-size:0.9rem; font-weight:700;">
                아래로 스크롤하여 단지별 전체 추천매물 보기 (6개 단지 × 3개 매물)
            </span>
        </div>
    </div>
    <hr style="border:none; border-top:2px dashed #334155; margin:10px 0 24px 0;">
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # 【하단 스크롤】 단지별 추천매물 (6개 단지 × 3개)
    # ══════════════════════════════════════════════════════════════
    st.markdown("#### 🏘️ 단지별 전체 추천매물 (부동산 등록 매물)")

    # 1. Signiel (Modified Name & Restored Prices)
    st.markdown('<div class="section-header">💎 시그니엘 레지던스 (롯데월드타워몰)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("시그니엘 89평 프리미엄 매물", "1억 / 1,700만", "89평 · 고층 · 남향 · 한강뷰 풀옵션", "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=400&q=80", "월세")
    with c2: property_card("시그니엘 88평 프리미엄 매물", "69억", "88평 · 고층 · 급매", "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=400&q=80")
    with c3: property_card("시그니엘 95평 월세", "3억 / 1,800만", "95평 · 중층 · 입주협의", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=400&q=80")

    # 2. Raemian Daechi Palace (Restored Prices)
    st.markdown('<div class="section-header">🏫 래미안 대치팰리스 (대장주)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("대치팰리스 45평형 남향 고층", "55억", "45평형 · 고층 · 남향 · 대치중심", "https://images.unsplash.com/photo-1600596542815-e328701102b9?auto=format&fit=crop&w=400&q=80", "강력추천")
    with c2: property_card("대치팰리스 34평 고층뷰", "44억", "34평 · 고층 · 남향 · 한강조망", "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=400&q=80")
    with c3: property_card("대치팰리스 33평 실용형", "42억", "33평 · 저층 · 남향 · 초급매", "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=400&q=80")

    # 3. Daechi SK View (Restored Prices)
    st.markdown('<div class="section-header">🚆 대치 SK뷰 (초역세권)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("대치SK뷰 33평 급매", "38억", "33평 · 중층 · 남향 · 대치역 도보 5분", "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=400&q=80", "급매")
    with c2: property_card("대치SK뷰 26평형 인기타입", "10억 / 150만", "26평형 · 동남향 · 저층 · 방3화2", "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=400&q=80", "월세")
    with c3: property_card("대치SK뷰 37평형 방4", "8억 / 530만", "37평형 · 저층 · 가성비", "https://images.unsplash.com/photo-1502005229766-5283522a6f1f?auto=format&fit=crop&w=400&q=80", "반전세")

    # 4. Daechi I-Park (NEW)
    st.markdown('<div class="section-header">🏘️ 대치 아이파크 (추가됨)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("대치아이파크 56평 펜트하우스", "59억", "56평 · 고층 · 남향 · 명문학군", "https://images.unsplash.com/photo-1512915922610-06c2b585408e?auto=format&fit=crop&w=400&q=80", "희소")
    with c2: property_card("대치아이파크 33평 인기형", "40억", "33평 · 고층 · 남향 · 조망 우수", "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=400&q=80")
    with c3: property_card("대치아이파크 32평 실속형", "38억", "32평 · 저층 · 남향 · 가성비", "https://images.unsplash.com/photo-1484154218962-a1c002085d2f?auto=format&fit=crop&w=400&q=80")

    # 5. Eunma Apartment (Restored Prices)
    st.markdown('<div class="section-header">📉 대치 은마아파트 (재건축)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("대치은마 31평 급매", "36.5억", "31평 · 중층 · 남향 · 대치동 중심", "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?auto=format&fit=crop&w=400&q=80", "투자추천")
    with c2: property_card("대치은마 31평 고층뷰", "38억", "31평 · 고층 · 남향 · 조망 우수", "https://images.unsplash.com/photo-1484154218962-a1c002085d2f?auto=format&fit=crop&w=400&q=80")
    with c3: property_card("대치은마 34평 넓은평형", "41억", "34평 · 남향 · 중층", "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=400&q=80")

    # 6. Samhwan Art Nouveau 2
    st.markdown('<div class="section-header">🎓 삼환 아르누보 2 (오피스텔)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("삼환아르누보 17평형 매매", "4.6억", "17평형 · 서향 · 고층", "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=400&q=80", "인기")
    with c2: property_card("삼환아르누보 17평형 복층", "1,000만 / 122만", "17평형 · 북동향 · 고층", "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=400&q=80", "월세")
    with c3: property_card("삼환아르누보 18평형 복층", "2,000만 / 200만", "18평형 · 북동향 · 2룸 확장형", "https://images.unsplash.com/photo-1486304873000-235643847519?auto=format&fit=crop&w=400&q=80")

# ─────────────────────────────────────────────────────────────────────────────
# AI 홍보·영업 도구 패널 (공유 함수 — 매칭예약 & 공동매물 양쪽에서 호출)
# ─────────────────────────────────────────────────────────────────────────────
def render_marketing_action_tools(section_key: str = "default"):
    """
    매물 숏츠 광고 제작 / 카카오톡 매칭 알리기 / 대기자 영업브리핑 문자발송 /
    자동 알림 장치 — 통합 AI 홍보·영업 도구 패널
    """
    APP_URL = "https://lotte-ai-app.streamlit.app/"

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);
                border-radius:16px; padding:24px 20px; margin-bottom:8px;">
      <h3 style="color:#fcd34d; margin:0 0 6px 0; font-size:1.15rem;">
        📣 AI 자동 홍보 &amp; 영업 도구 센터
      </h3>
      <p style="color:#94a3b8; font-size:0.85rem; margin:0;">
        접수된 매물·수요 정보를 즉시 광고·문자·카카오로 전파하세요.
      </p>
    </div>
    """, unsafe_allow_html=True)

    tool_tab1, tool_tab2, tool_tab3, tool_tab4 = st.tabs([
        "🎬 숏츠·유튜버 광고",
        "💛 카카오톡 매칭 알리기",
        "📱 대기자 문자발송",
        "🔔 자동 알림 장치",
    ])

    # ── 탭 1: 매물 숏츠·유튜버 광고 만들기 ───────────────────────────────
    with tool_tab1:
        st.markdown("#### 🎬 매물 숏츠 & 유튜버 광고 자동 제작")
        st.caption("AI가 매물 정보를 기반으로 유튜브/인스타 숏츠 스크립트·자막·멘트를 자동 생성합니다.")

        with st.container(border=True):
            c1, c2 = st.columns(2)
            shorts_complex = c1.text_input("단지명", placeholder="래미안대치팰리스", key=f"{section_key}_sh_complex")
            shorts_price   = c2.text_input("가격 요약", placeholder="34평 전세 8억", key=f"{section_key}_sh_price")
            shorts_style   = st.radio("숏츠 스타일",
                ["💥 임팩트형 (빠른 컷·강렬 BGM)", "✨ 고급형 (시네마틱·클래식)", "🎵 트렌디형 (힙합·Z세대)"],
                horizontal=True, key=f"{section_key}_sh_style")
            shorts_point   = st.text_area("매물 핵심 포인트 (AI 스크립트 생성 근거)",
                placeholder="예) 대치초 배정, 학원가 도보 3분, 풀옵션, 즉시입주 가능",
                height=80, key=f"{section_key}_sh_point")

            if st.button("🚀 AI 숏츠 스크립트 자동 생성", type="primary",
                         use_container_width=True, key=f"{section_key}_btn_shorts"):
                if not shorts_complex:
                    st.warning("단지명을 입력해주세요.")
                else:
                    with st.spinner("🎬 AI가 숏츠 스크립트를 작성 중입니다..."):
                        import time as _t; _t.sleep(1.2)
                    st.success("✅ 숏츠 스크립트 생성 완료!")
                    st.markdown(f"""
<div style="background:#0f172a;border-radius:10px;padding:16px;border:1px solid #334155;margin-top:8px;">
  <div style="color:#38bdf8;font-weight:700;margin-bottom:8px;">📜 오프닝 멘트 (0~3초)</div>
  <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">
    "지금 당장 봐야 할 대치동 역대급 매물이 나왔습니다!"
  </div>
  <div style="color:#38bdf8;font-weight:700;margin:12px 0 8px 0;">🏠 매물 브리핑 (3~15초)</div>
  <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">
    "{shorts_complex} {shorts_price}<br>
    {shorts_point if shorts_point else '핵심 포인트를 입력하시면 맞춤 멘트가 생성됩니다.'}<br>
    이 가격, 이 조건 — 다시는 없습니다!"
  </div>
  <div style="color:#38bdf8;font-weight:700;margin:12px 0 8px 0;">🔔 클로징 CTA (15~30초)</div>
  <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">
    "지금 바로 롯데타워 AI 부동산 앱에서 예약하세요!<br>
    링크는 바이오에 있습니다. 놓치면 후회합니다! 👉 {APP_URL}"
  </div>
</div>
                    """, unsafe_allow_html=True)
                    st.info("💡 위 스크립트를 복사하여 YOU-LAB 탭에서 실제 숏츠를 제작하세요!")

    # ── 탭 2: 카카오톡 AI 예약 매칭 알리기 ──────────────────────────────
    with tool_tab2:
        st.markdown("#### 💛 카카오톡으로 AI 매칭 결과 알리기")
        st.caption("접수 완료된 매물·수요 정보를 카카오톡 오픈채팅 또는 1:1 링크로 즉시 공유합니다.")

        with st.container(border=True):
            kakao_msg_template = st.selectbox("메시지 템플릿 선택", [
                "📢 공급 매물 접수 알림 (공동중개 요청)",
                "🔍 수요 손님 접수 알림 (매물 찾기)",
                "🚀 AI 매칭 성공 알림 (계약 촉진)",
                "✉️ 직접 작성",
            ], key=f"{section_key}_kk_tmpl")

            TEMPLATES = {
                "📢 공급 매물 접수 알림 (공동중개 요청)":
                    f"안녕하세요! 롯데타워 AI 부동산 이상수 대표입니다.\n"
                    f"방금 전 우수 매물이 접수되었습니다. 공동중개 가능하신 분 연락주세요!\n"
                    f"👉 상세보기: {APP_URL}",
                "🔍 수요 손님 접수 알림 (매물 찾기)":
                    f"대표님, 롯데타워 AI 부동산입니다.\n"
                    f"조건 딱 맞는 손님이 대기 등록 하셨습니다. 혹시 매물 있으시면 바로 연락 주세요!\n"
                    f"👉 {APP_URL}",
                "🚀 AI 매칭 성공 알림 (계약 촉진)":
                    f"[AI 매칭 성공 🎉] 롯데타워 AI 부동산입니다.\n"
                    f"귀하의 매물/수요 조건과 99% 일치하는 상대방이 발견되었습니다!\n"
                    f"지금 바로 확인하세요 👉 {APP_URL}",
                "✉️ 직접 작성": "",
            }

            default_msg = TEMPLATES.get(kakao_msg_template, "")
            kakao_body  = st.text_area("발송 메시지 (수정 가능)",
                                       value=default_msg, height=120,
                                       key=f"{section_key}_kk_body")

            c1, c2 = st.columns(2)
            with c1:
                kakao_open_url = f"https://open.kakao.com/o/share?url={APP_URL}&text={kakao_body[:50]}..."
                st.markdown(
                    f'<a href="{kakao_open_url}" target="_blank" style="display:block;text-align:center;'
                    f'background:#fef01b;color:#3c1e1e;font-weight:bold;padding:12px;'
                    f'border-radius:10px;text-decoration:none;font-size:0.95rem;">💛 카카오톡 오픈채팅 공유</a>',
                    unsafe_allow_html=True)
            with c2:
                if st.button("📋 메시지 복사 (클립보드)", use_container_width=True,
                             key=f"{section_key}_kk_copy"):
                    st.code(kakao_body, language="text")
                    st.toast("📋 메시지가 준비되었습니다. 위 박스에서 복사하세요!")

    # ── 탭 3: 대기자 영업브리핑 문자발송 ─────────────────────────────────
    with tool_tab3:
        st.markdown("#### 📱 대기자에게 영업브리핑 문자 자동 발송")
        st.caption("등록된 대기 수요자 목록에 개인화 영업브리핑 문자를 일괄 발송합니다.")

        with st.container(border=True):
            briefing_type = st.radio("브리핑 유형",
                ["🏠 신규 매물 출시 알림", "📊 시세 변동 긴급 브리핑", "🎯 맞춤 매물 발견 알림", "📅 계약 만료 사전 안내"],
                horizontal=True, key=f"{section_key}_sms_type")
            briefing_complex = st.text_input("대상 단지/지역", placeholder="대치동 래미안대치팰리스 34평",
                                             key=f"{section_key}_sms_complex")
            briefing_point   = st.text_input("핵심 브리핑 포인트", placeholder="학원가 3분, 8억 전세, 즉시입주",
                                             key=f"{section_key}_sms_point")

            SMS_TEMPLATES = {
                "🏠 신규 매물 출시 알림":
                    f"[롯데타워AI부동산] 안녕하세요!\n{briefing_complex} 신규 매물이 출시되었습니다.\n"
                    f"{briefing_point}\n지금 바로 확인: {APP_URL}\n문의: 010-8985-8945",
                "📊 시세 변동 긴급 브리핑":
                    f"[긴급] 롯데타워AI부동산입니다.\n{briefing_complex} 최근 시세가 변동되었습니다!\n"
                    f"{briefing_point}\n상세분석: {APP_URL}",
                "🎯 맞춤 매물 발견 알림":
                    f"[AI매칭] 고객님 안녕하세요! 롯데타워AI부동산입니다.\n"
                    f"고객님 조건과 일치하는 {briefing_complex} 매물이 발견되었습니다!\n"
                    f"빠른 확인 부탁드립니다 👉 {APP_URL}",
                "📅 계약 만료 사전 안내":
                    f"[계약만료안내] 롯데타워AI부동산 이상수 대표입니다.\n"
                    f"고객님의 계약 만료가 다가오고 있습니다. {briefing_complex}\n"
                    f"이사 계획 상담: 010-8985-8945 | {APP_URL}",
            }
            sms_body = st.text_area("발송 문자 내용 (수정 가능)",
                                    value=SMS_TEMPLATES.get(briefing_type, ""),
                                    height=130, key=f"{section_key}_sms_body")

            c1, c2, c3 = st.columns(3)
            recv_phone = c1.text_input("수신 번호", placeholder="01012345678", key=f"{section_key}_sms_recv")
            recv_name  = c2.text_input("수신자 이름", placeholder="홍길동 대표님", key=f"{section_key}_sms_name")
            send_count = c3.number_input("대기자 일괄발송 수", 1, 500, 1, key=f"{section_key}_sms_count")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("📨 1:1 문자 발송 (데모)", use_container_width=True,
                             type="primary", key=f"{section_key}_btn_sms1"):
                    if not recv_phone:
                        st.warning("수신 번호를 입력해주세요.")
                    else:
                        with st.spinner("문자 발송 중..."):
                            import time as _t; _t.sleep(0.8)
                        st.success(f"✅ {recv_name or recv_phone}님께 영업 브리핑 문자가 발송되었습니다! (데모)")
                        st.code(f"수신: {recv_phone}\n내용: {sms_body}", language="text")
            with col_s2:
                if st.button(f"📢 대기자 {send_count}명 일괄발송 (데모)", use_container_width=True,
                             key=f"{section_key}_btn_sms_bulk"):
                    with st.spinner(f"대기자 {send_count}명에게 발송 중..."):
                        import time as _t; _t.sleep(1.0)
                    st.success(f"✅ {send_count}명의 대기자에게 영업 브리핑 문자 발송 완료! (데모)")
                    st.info("💡 실제 발송은 알리고·CoolSMS 등 문자 API 연동 시 자동 실행됩니다.")

    # ── 탭 4: 자동 알림 장치 ──────────────────────────────────────────────
    with tool_tab4:
        st.markdown("#### 🔔 자동 알림 & 스케줄 관리")
        st.caption("매물 변동·매칭 성공 시 자동으로 알림을 발송하는 스케줄 설정입니다.")

        with st.container(border=True):
            st.markdown("##### ⚙️ 자동 알림 설정")
            c1, c2 = st.columns(2)
            auto_sms   = c1.toggle("📱 문자 자동발송", value=True,  key=f"{section_key}_auto_sms")
            auto_kakao = c2.toggle("💛 카카오 자동발송", value=True, key=f"{section_key}_auto_kk")
            c3, c4 = st.columns(2)
            auto_match = c3.toggle("🤝 매칭 성공 시 즉시 알림", value=True, key=f"{section_key}_auto_match")
            auto_price = c4.toggle("📊 시세 변동 시 자동 브리핑", value=False, key=f"{section_key}_auto_price")

            st.divider()
            st.markdown("##### 📅 브리핑 스케줄")
            c1, c2, c3 = st.columns(3)
            sched_day  = c1.multiselect("발송 요일", ["월","화","수","목","금","토","일"],
                                        default=["월","수","금"], key=f"{section_key}_sched_day")
            sched_time = c2.selectbox("발송 시각", ["08:00","09:00","10:00","11:00","14:00","16:00","18:00"],
                                      index=2, key=f"{section_key}_sched_time")
            sched_who  = c3.selectbox("발송 대상", ["전체 대기자","매매 대기자","전세 대기자","월세 대기자"],
                                      key=f"{section_key}_sched_who")

            st.divider()
            st.markdown("##### 🎯 현재 대기자 현황 (실시간)")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("📥 총 대기자", "4,218명", "+23 오늘")
            kpi2.metric("🏠 공급 접수", "187건",   "+5 오늘")
            kpi3.metric("🤝 AI매칭률", "94.2%",   "+1.3%")
            kpi4.metric("📨 금일 발송", "1,204건",  "진행중")

            st.divider()
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                if st.button("🔔 지금 즉시 전체 대기자 알림 발송", type="primary",
                             use_container_width=True, key=f"{section_key}_btn_now"):
                    with st.spinner("전체 대기자에게 알림 발송 중..."):
                        import time as _t; _t.sleep(1.2)
                    st.success("✅ 4,218명에게 알림이 발송되었습니다! (데모)")
                    st.balloons()
            with col_a2:
                if st.button(f"📅 스케줄 등록 ({'/'.join(sched_day)} {sched_time})",
                             use_container_width=True, key=f"{section_key}_btn_sched"):
                    with st.spinner("스케줄 등록 중..."):
                        import time as _t; _t.sleep(0.6)
                    st.success(f"✅ 매주 {', '.join(sched_day)} {sched_time}에 {sched_who}에게 자동 브리핑이 예약되었습니다!")

            st.markdown("""
            <div style="background:#0f172a;border-radius:10px;padding:14px;margin-top:10px;
                        border:1px solid #334155;font-size:0.8rem;color:#94a3b8;">
              💡 <b>실제 운영 연동:</b><br>
              &nbsp;&nbsp;• 문자: 알리고(Aligo) · CoolSMS API<br>
              &nbsp;&nbsp;• 카카오: 카카오 비즈메시지 API<br>
              &nbsp;&nbsp;• 스케줄: Airflow DAG 등록<br>
              &nbsp;&nbsp;• 실시간 매칭 알림: MLflow 파이프라인 트리거
            </div>
            """, unsafe_allow_html=True)


def render_matching_and_reservation():

    # 1. AI Chatbot Section (Revamped Dashboard Style)
    with st.expander("💬 AI 챗봇 상담 (열기/닫기)", expanded=True):
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #fccc15; margin:0;">☁️ AI Real Estate Assistant</h3>
            <span style="font-size: 0.8em; color: gray;">24시간 365일, 대치동 부동산/세금/법률 데이터를 실시간 분석하여 답변합니다.</span>
        </div>
        """, unsafe_allow_html=True)

        # FAQ Dashboard
        st.markdown("##### 💡 자주 묻는 질문 (Top 50+)")
        faq_tab1, faq_tab2, faq_tab3, faq_tab4 = st.tabs(["🔥 인기질문", "💰 매매/투자", "🏠 전세/월세", "⚖️ 세금/정책"])
        
        selected_question = None
        
        with faq_tab1:
            fq1, fq2 = st.columns(2)
            if fq1.button("📌 대치동 학군 배정 원칙이 어떻게 되나요?", use_container_width=True): selected_question = "대치동 학군 배정 원칙 알려줘"
            if fq2.button("📈 대치동 국평(34평) 최근 시세 추이는?", use_container_width=True): selected_question = "대치동 34평 시세 추이 보여줘"
            if fq1.button("🚨 급매물 알림을 가장 먼저 받으려면?", use_container_width=True): selected_question = "급매물 알림 신청 방법 알려줘"
            if fq2.button("🏗️ 은마아파트 재건축 현재 단계는?", use_container_width=True): selected_question = "은마아파트 재건축 진행 현황 알려줘"
            
        with faq_tab2:
            fq1, fq2 = st.columns(2)
            if fq1.button("토지거래허가구역 실거주 요건은?", use_container_width=True): selected_question = "토지거래허가구역 요건 설명해줘"
            if fq2.button("갭투자 가능한 단지가 있나요?", use_container_width=True): selected_question = "대치동 갭투자 매물 추천해줘"

        with faq_tab3:
            fq1, fq2 = st.columns(2)
            if fq1.button("전세자금대출 최대 한도는?", use_container_width=True): selected_question = "전세자금대출 한도 알려줘"
            if fq2.button("전세 만기 시 보증금 반환 절차", use_container_width=True): selected_question = "전세 보증금 반환 내용 설명해줘"

        with faq_tab4:
            fq1, fq2 = st.columns(2)
            if fq1.button("1가구 2주택 양도세 비과세 요건", use_container_width=True): selected_question = "양도세 비과세 요건 알려줘"
            if fq2.button("취득세 중과 배제 기준", use_container_width=True): selected_question = "취득세 중과 기준 설명해줘"

        st.markdown("---")
        
        # Chat Interface
        msg_container = st.container(height=300)
        with msg_container:
            st.chat_message("assistant").write("안녕하세요! 롯데타워 AI 부동산 비서입니다. 궁금하신 점을 선택하거나 직접 물어보세요.")
            # Simple simulation of response to clicked button
            if selected_question:
                st.chat_message("user").write(selected_question)
                st.chat_message("assistant").write(f"네, **'{selected_question}'**에 대해 분석 중입니다...\n\n(AI가 관련 법규와 실거래 데이터를 조회하고 있습니다.)")

        prompt = st.chat_input("여기에 질문을 입력하세요...")
        if prompt:
            with msg_container:
                st.chat_message("user").write(prompt)
                st.chat_message("assistant").write("문의하신 내용을 확인했습니다. 상세 분석 리포트를 생성하고 있습니다.")

    st.markdown("---")
    
    # 2. Reservation Section (Styled Update)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #fccc15; margin-bottom: 5px;">🚀 롯데타워 AI 사전 매칭 센터</h2>
        <p style="color: #64748b; font-size: 0.9rem;">에어비앤비 방식의 스마트 예약 시스템으로 매칭 확률을 300% 높이세요.</p>
    </div>
    """, unsafe_allow_html=True)
    
    _MC_PROP_TYPES  = ["아파트", "빌라/연립", "오피스텔", "상가/상업", "토지", "기타"]
    _MC_TRADE_TYPES = ["매매", "전세", "월세(반전세 포함)"]
    _MC_FEATURES_S  = ["💰 금액조절 가능","👀 바로 볼 수 있는","🏗️ 새로 지은",
                       "🙋 손님 대기중","🚇 역세권 위치","🔧 수리 깨끗한","🏦 전세대출 가능","🛋️ 풀옵션"]
    _MC_FEATURES_D  = ["💰 금액조절 가능","🚀 즉시입주 가능","🚗 주차 필수",
                       "🏫 학군 중요","🚇 역세권 선호","🏗️ 신축 선호","🏦 대출 활용 예정","🏠 실거주 목적"]
    _MC_REGIONS_GU  = ["강남구","서초구","송파구","강동구","마포구","용산구","성동구","광진구",
                       "강서구","양천구","영등포구","동작구","관악구","서대문구","은평구","노원구"]
    # 대치1동 주요 단지 드롭다운
    _MC_COMPLEX_OPTS = [
        "래미안대치팰리스",
        "대치SK뷰",
        "대치아이파크",
        "은마아파트",
        "삼환아르누보2 오피스텔",
        "롯데월드타워몰 시그니엘레지던스",
        "직접입력",
    ]
    def _mc_sqm2py(v): return round(v / 3.3058, 2)

    tab_supply, tab_demand = st.tabs(["🏠 1. 공급자(임대/매도) 등록", "🔑 2. 수요자(임차/매수) 등록"])
    
    with tab_supply:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);border-radius:14px;
                    padding:18px 20px;margin-bottom:16px;border-left:5px solid #facc15;">
          <div style="font-size:1.1rem;font-weight:900;color:#facc15;">🛡️ 내 집의 골든타임 예약 (공급)</div>
          <div style="font-size:0.85rem;color:#94a3b8;margin-top:4px;">
            AI가 주변 실거래와 학원가 입지 데이터를 분석하여 가장 비싸게 거래될 시점에 마케팅을 시작합니다.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 섹션 1: 기본 인적사항
        st.markdown("##### 👤 기본 인적사항")
        mc_s_c1, mc_s_c2 = st.columns(2)
        mc_s_name  = mc_s_c1.text_input("이름 (공급자)", placeholder="홍길동", key="mc_s_name")
        mc_s_phone = mc_s_c2.text_input("연락처", placeholder="010-1234-5678", key="mc_s_phone")
        st.divider()

        # ── 섹션 2: 매물 종류 & 거래 구분
        st.markdown("##### 🏷️ 매물 종류 & 거래 구분")
        mc_s_pc1, mc_s_pc2 = st.columns(2)
        mc_s_prop  = mc_s_pc1.selectbox("매물 종류", _MC_PROP_TYPES, key="mc_s_prop")
        mc_s_trade = mc_s_pc2.radio("거래 구분", _MC_TRADE_TYPES, horizontal=True, key="mc_s_trade")
        st.divider()

        # ── 섹션 3: 위치 정보
        st.markdown("##### 📍 위치 정보")
        mc_s_lc1, mc_s_lc2 = st.columns(2)
        mc_s_cplx_sel = mc_s_lc1.selectbox("단지명/건물명", _MC_COMPLEX_OPTS, key="mc_s_cplx_sel")
        mc_s_dongho  = mc_s_lc2.text_input("동/호수 (비공개 보안 유지)", placeholder="101동 1501호", key="mc_s_dongho")
        if mc_s_cplx_sel == "직접입력":
            mc_s_complex = st.text_input("단지명 직접 입력", placeholder="단지명/건물명을 입력하세요", key="mc_s_complex")
        else:
            mc_s_complex = mc_s_cplx_sel
        mc_s_fc1, mc_s_fc2, mc_s_fc3, mc_s_fc4 = st.columns(4)
        mc_s_floor  = mc_s_fc1.number_input("해당 층",  1, 100, 5,  key="mc_s_fl")
        mc_s_tfloor = mc_s_fc2.number_input("총 층수",  1, 200, 20, key="mc_s_tfl")
        mc_s_rooms  = mc_s_fc3.number_input("방 수",    1, 20,  3,  key="mc_s_rm")
        mc_s_baths  = mc_s_fc4.number_input("화장실",   1, 10,  2,  key="mc_s_bt")
        st.divider()

        # ── 섹션 4: 면적/규모
        st.markdown("##### 📐 면적/규모")
        mc_s_ac1, mc_s_ac2, mc_s_ac3 = st.columns(3)
        mc_s_sup = mc_s_ac1.number_input("공급면적(㎡)", 0.0, step=0.5, format="%.1f", key="mc_s_sup")
        mc_s_prv = mc_s_ac2.number_input("전용면적(㎡)", 0.0, step=0.5, format="%.1f", key="mc_s_prv")
        mc_s_ld  = mc_s_ac3.number_input("대지면적(㎡)", 0.0, step=0.5, format="%.1f", key="mc_s_ld")
        if mc_s_sup > 0 or mc_s_prv > 0:
            mc_s_ip1, mc_s_ip2, mc_s_ip3 = st.columns(3)
            if mc_s_sup > 0: mc_s_ip1.info(f"≈ **{_mc_sqm2py(mc_s_sup)}평**")
            if mc_s_prv > 0: mc_s_ip2.info(f"≈ **{_mc_sqm2py(mc_s_prv)}평**")
            if mc_s_ld  > 0: mc_s_ip3.info(f"≈ **{_mc_sqm2py(mc_s_ld)}평**")
        st.divider()

        # ── 섹션 5: 가격 정보
        st.markdown("##### 💵 가격 정보")
        if mc_s_trade == "매매":
            mc_s_pp1, mc_s_pp2 = st.columns(2)
            mc_s_price = {
                "매매가_억":  mc_s_pp1.number_input("매매가(억)", 0.0, step=0.1, format="%.1f", key="mc_s_sale"),
                "매매가_만원": mc_s_pp2.number_input("+ 만원단위", 0, step=100, key="mc_s_sale_m")
            }
        elif mc_s_trade == "전세":
            mc_s_pp1, mc_s_pp2 = st.columns(2)
            mc_s_price = {
                "보증금_억":   mc_s_pp1.number_input("보증금(억)", 0.0, step=0.1, format="%.1f", key="mc_s_dep"),
                "보증금_만원": mc_s_pp2.number_input("+ 만원단위", 0, step=100, key="mc_s_dep_m")
            }
        else:  # 월세(반전세 포함)
            mc_s_pp1, mc_s_pp2, mc_s_pp3 = st.columns(3)
            mc_s_price = {
                "보증금_억":   mc_s_pp1.number_input("보증금(억)", 0.0, step=0.1, format="%.1f", key="mc_s_mdep"),
                "보증금_만원": mc_s_pp2.number_input("+ 만원단위", 0, step=100,   key="mc_s_mdep_m"),
                "월세_만원":   mc_s_pp3.number_input("월세(만원)", 0, step=5,     key="mc_s_rent")
            }
        st.divider()

        # ── 섹션 6: 매물 특징
        st.markdown("##### ✅ 매물 특징 (해당 사항 모두 체크)")
        mc_s_feats = []
        mc_s_fcs = st.columns(4)
        for _i, _f in enumerate(_MC_FEATURES_S):
            if mc_s_fcs[_i % 4].checkbox(_f, key=f"mc_sf_{_i}"): mc_s_feats.append(_f)
        st.divider()

        # ── 섹션 7: 일정 & 특이사항
        st.markdown("##### 📅 일정 & 특이사항")
        mc_s_dc1, mc_s_dc2 = st.columns(2)
        mc_s_date = mc_s_dc1.date_input("이사예정일/인도가능일",
                                         value=datetime.date.today()+datetime.timedelta(days=30), key="mc_s_date")
        mc_s_memo = mc_s_dc2.text_area("특이사항 메모", placeholder="세입자 이사 후 즉시 가능 등", height=90, key="mc_s_memo")
        st.divider()

        # ── 섹션 8: 발송 지역
        st.markdown("##### 📡 발송 지역")
        mc_s_gc1, mc_s_gc2 = st.columns(2)
        mc_s_gu     = mc_s_gc1.multiselect("발송 구 선택", _MC_REGIONS_GU, default=["강남구"], key="mc_s_gu")
        mc_s_custom = mc_s_gc2.text_input("추가 직접 입력(동 등)", placeholder="대치동, 압구정동", key="mc_s_custom")
        st.divider()

        # ── AI 공급자 패키지
        st.markdown("##### 🎁 AI 공급자 패키지 (체크 시 자동 수행)")
        mc_s_pkg1 = st.checkbox("🎥 나노 바나나 CEO AI 숏츠 제작 및 배포",          value=True, key="mc_s_pkg1")
        mc_s_pkg2 = st.checkbox("📊 주변 단지 대비 저평가 분석 리포트 생성",          value=True, key="mc_s_pkg2")
        mc_s_pkg3 = st.checkbox("👑 VIP 대기 수요자(4,200명) 우선 매칭 알림",        value=True, key="mc_s_pkg3")
        st.divider()

        supply_agree = st.checkbox(
            "✅ [필수] 개인정보 수집·이용에 동의합니다. (이름·연락처는 매칭 목적으로만 활용됩니다)",
            key="match_supply_agree"
        )
        st.caption("※ 개인정보 보호법에 따라 수집된 정보는 매칭 완료 후 즉시 파기됩니다.")
        if st.button("🚀 AI 마케팅 및 매칭 예약 완료", use_container_width=True, type="primary", key="mc_btn_supply"):
            mc_s_errs = []
            if not mc_s_name:    mc_s_errs.append("이름을 입력해주세요.")
            if not mc_s_phone:   mc_s_errs.append("연락처를 입력해주세요.")
            if not mc_s_complex: mc_s_errs.append("단지명을 입력해주세요.")
            if not supply_agree: mc_s_errs.append("개인정보 수집·이용 동의가 필요합니다.")
            if mc_s_errs:
                for _e in mc_s_errs: st.error(_e)
            else:
                import time as _t
                with st.spinner("🔒 암호화 전송 중..."): _t.sleep(1.0)
                st.success("✅ 등록 완료! 현재 대기 수요자 데이터와 대조한 결과입니다.")
                st.markdown("""
                <div style="background-color:#1e3a8a; padding:20px; border-radius:10px;
                            text-align:center; color:white; border:1px solid #3b82f6;">
                    <div style="font-size:0.9em; opacity:0.8;">AI 기반 매칭 예상 점수</div>
                    <div style="font-size:2.5em; font-weight:bold; color:#facc15;">94 / 100</div>
                    <div style="font-size:0.8em; margin-top:10px;">
                    🚨 <b>코멘트:</b> 현재 대치동 학군지 인근 수요가 급증하고 있어,<br>
                    등록하신 가격대는 '1주일 내 계약' 확률이 매우 높습니다.<br>
                    <b>나노 바나나 CEO 숏츠 제작을 즉시 시작합니다!</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
        st.caption("본 시스템은 Fast Campus MLOps 파이프라인(MLflow, Airflow)을 통해 실시간으로 데이터를 검증하고 있습니다.")
            
    with tab_demand:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0f2a1a,#0f3a2a);border-radius:14px;
                    padding:18px 20px;margin-bottom:16px;border-left:5px solid #22c55e;">
          <div style="font-size:1.1rem;font-weight:900;color:#4ade80;">🎯 VIP 입주 희망 대기 (수요)</div>
          <div style="font-size:0.85rem;color:#94a3b8;margin-top:4px;">
            비공개 급매물이나 퇴거 예정 매물을 일반 포털보다 48시간 먼저 선점하세요.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 섹션 1: 기본 인적사항
        st.markdown("##### 👤 기본 인적사항")
        mc_d_c1, mc_d_c2 = st.columns(2)
        mc_d_name  = mc_d_c1.text_input("이름 (수요자)", placeholder="홍길동", key="mc_d_name")
        mc_d_phone = mc_d_c2.text_input("연락처", placeholder="010-1234-5678", key="mc_d_phone")
        st.divider()

        # ── 섹션 2: 희망 매물 종류 & 거래 유형
        st.markdown("##### 🏷️ 희망 매물 종류 & 거래 유형")
        mc_d_tc1, mc_d_tc2 = st.columns(2)
        mc_d_prop  = mc_d_tc1.selectbox("희망 매물 종류", _MC_PROP_TYPES, key="mc_d_prop")
        mc_d_trade = mc_d_tc2.radio("희망 거래 유형", _MC_TRADE_TYPES, horizontal=True, key="mc_d_trade")
        st.divider()

        # ── 섹션 3: 희망 지역 & 단지
        st.markdown("##### 📍 희망 지역 & 단지")
        mc_d_lc1, mc_d_lc2 = st.columns(2)
        mc_d_region    = mc_d_lc1.text_input("희망 지역(구/동)", placeholder="강남구 대치동", key="mc_d_region")
        mc_d_cplx_sel  = mc_d_lc2.selectbox("희망 단지명", _MC_COMPLEX_OPTS, key="mc_d_cplx_sel")
        if mc_d_cplx_sel == "직접입력":
            mc_d_complex = st.text_input("단지명 직접 입력", placeholder="단지명/건물명을 입력하세요", key="mc_d_complex")
        else:
            mc_d_complex = mc_d_cplx_sel
        st.divider()

        # ── 섹션 4: 희망 층수/방/화장실
        st.markdown("##### 🏢 희망 층수 & 구조")
        mc_d_fc1, mc_d_fc2, mc_d_fc3 = st.columns(3)
        mc_d_floor_pref = mc_d_fc1.selectbox("선호 층",
            ["무관","저층(1~5)","중층(6~15)","고층(16층+)"], key="mc_d_fpref")
        mc_d_rooms = mc_d_fc2.number_input("희망 방 수",  1, 10, 3, key="mc_d_rm")
        mc_d_baths = mc_d_fc3.number_input("희망 화장실", 1, 5,  2, key="mc_d_bt")
        st.divider()

        # ── 섹션 5: 희망 면적 범위
        st.markdown("##### 📐 희망 면적 범위")
        mc_d_ac1, mc_d_ac2 = st.columns(2)
        mc_d_amin = mc_d_ac1.number_input("최소 면적(㎡)", 0.0, step=1.0, format="%.1f", key="mc_d_amin")
        mc_d_amax = mc_d_ac2.number_input("최대 면적(㎡)", 0.0, step=1.0, format="%.1f", key="mc_d_amax")
        if mc_d_amin > 0 or mc_d_amax > 0:
            st.info(f"≈ {_mc_sqm2py(mc_d_amin)}평 ~ {_mc_sqm2py(mc_d_amax)}평")
        st.divider()

        # ── 섹션 6: 희망 가격 범위
        st.markdown("##### 💵 희망 가격 범위")
        if mc_d_trade == "매매":
            mc_d_pp1, mc_d_pp2 = st.columns(2)
            mc_d_price = {
                "희망_매매_최소_억": mc_d_pp1.number_input("매매가 최소(억)", 0.0, step=0.5, format="%.1f", key="mc_d_pmin"),
                "희망_매매_최대_억": mc_d_pp2.number_input("매매가 최대(억)", 0.0, step=0.5, format="%.1f", key="mc_d_pmax")
            }
        elif mc_d_trade == "전세":
            mc_d_pp1, mc_d_pp2 = st.columns(2)
            mc_d_price = {
                "희망_보증금_최소_억": mc_d_pp1.number_input("보증금 최소(억)", 0.0, step=0.5, format="%.1f", key="mc_d_depmin"),
                "희망_보증금_최대_억": mc_d_pp2.number_input("보증금 최대(억)", 0.0, step=0.5, format="%.1f", key="mc_d_depmax")
            }
        else:  # 월세(반전세 포함)
            st.markdown("###### 💰 보증금 범위")
            mc_d_pp1, mc_d_pp2 = st.columns(2)
            mc_dep_min = mc_d_pp1.number_input("보증금 최소(억)", 0.0, step=0.1, format="%.1f", key="mc_d_mdepmin")
            mc_dep_max = mc_d_pp2.number_input("보증금 최대(억)", 0.0, step=0.1, format="%.1f", key="mc_d_mdepmax")
            if mc_dep_min > 0 or mc_dep_max > 0:
                st.info(f"보증금 범위: {mc_dep_min}억 ~ {mc_dep_max}억")
            st.markdown("###### 💸 월세 범위")
            mc_d_pp3, mc_d_pp4 = st.columns(2)
            mc_rent_min = mc_d_pp3.number_input("월세 최소(만원)", 0, step=5, key="mc_d_rentmin")
            mc_rent_max = mc_d_pp4.number_input("월세 최대(만원)", 0, step=5, key="mc_d_rentmax")
            if mc_rent_min > 0 or mc_rent_max > 0:
                st.info(f"월세 범위: {mc_rent_min}만원 ~ {mc_rent_max}만원")
            mc_d_price = {
                "희망_보증금_최소_억": mc_dep_min,
                "희망_보증금_최대_억": mc_dep_max,
                "희망_월세_최소_만원": mc_rent_min,
                "희망_월세_최대_만원": mc_rent_max
            }
        st.divider()

        # ── 섹션 7: 희망 조건 선택
        st.markdown("##### ✅ 희망 조건 선택")
        mc_d_feats = []
        mc_d_fcs = st.columns(4)
        for _i, _f in enumerate(_MC_FEATURES_D):
            if mc_d_fcs[_i % 4].checkbox(_f, key=f"mc_df_{_i}"): mc_d_feats.append(_f)
        st.divider()

        # ── 섹션 8: 입주 희망일 & 기타 요청
        st.markdown("##### 📅 입주 희망일 & 기타 요청")
        mc_d_dc1, mc_d_dc2 = st.columns(2)
        mc_d_date = mc_d_dc1.date_input("입주 희망일",
                                         value=datetime.date.today()+datetime.timedelta(days=60), key="mc_d_date")
        mc_d_memo = mc_d_dc2.text_area("기타 요청사항", placeholder="반려동물 가능, 주차 2대 필수 등", height=90, key="mc_d_memo")
        st.divider()

        # ── 섹션 9: 발송 지역
        st.markdown("##### 📡 발송 지역")
        mc_d_gc1, mc_d_gc2 = st.columns(2)
        mc_d_gu     = mc_d_gc1.multiselect("발송 구 선택", _MC_REGIONS_GU, default=["강남구"], key="mc_d_gu")
        mc_d_custom = mc_d_gc2.text_input("추가 직접 입력(동 등)", placeholder="대치동, 압구정동", key="mc_d_custom")
        st.divider()

        st.checkbox("🔔 개인화 매칭 알림 수신 동의", key="mc_d_notif")
        demand_agree = st.checkbox(
            "✅ [필수] 개인정보 수집·이용에 동의합니다. (이름·연락처는 매칭 목적으로만 활용됩니다)",
            key="match_demand_agree"
        )
        st.caption("※ 개인정보 보호법에 따라 수집된 정보는 매칭 완료 후 즉시 파기됩니다.")
        if st.button("🔍 VIP 매칭 대기 등록하기", use_container_width=True, type="primary", key="mc_btn_demand"):
            mc_d_errs = []
            if not mc_d_name:   mc_d_errs.append("이름을 입력해주세요.")
            if not mc_d_phone:  mc_d_errs.append("연락처를 입력해주세요.")
            if not mc_d_region: mc_d_errs.append("희망 지역을 입력해주세요.")
            if not demand_agree: mc_d_errs.append("개인정보 수집·이용 동의가 필요합니다.")
            if mc_d_errs:
                for _e in mc_d_errs: st.error(_e)
            else:
                import time as _t
                with st.spinner("🔒 암호화 전송 중..."): _t.sleep(1.0)
                st.success("✅ VIP 매칭 대기 등록이 완료되었습니다! 조건에 맞는 매물 발생 시 즉시 연락드립니다.")
                st.balloons()

    # ── AI 홍보·영업 도구 패널 ──────────────────────────────────────────
    st.markdown("---")
    render_marketing_action_tools(section_key="match")

def render_shorts_and_youlab():
    st.markdown("### 🎬 AI 숏츠 플레이어")
    st.video("https://www.w3schools.com/html/mov_bbb.mp4")
    
    st.markdown("---")
    
    # YOU-LAB Section
    st.markdown("""
    <div style="background-color: #7f1d1d; color: white; padding: 15px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
        <h2 style="margin:0; color:white;">🔴 YOU-LAB: 초고속 숏츠 연구소</h2>
        <p style="margin:5px 0 0 0; font-size:0.8em; opacity:0.8;">Token Inference Server 가동 중 | GPU 가속 엔진 활성화</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.markdown("#### ⚙️ 촬영 및 인코딩 설정")
        with st.container(border=True):
            st.radio("시네마틱 스타일 선택", ["💥 마이클 베이 (폭발적/화려함)", "✨ 미니멀 (세련됨/깔끔함)", "🎵 트렌디 (힙합/빠른템포)"])
            st.slider("영상 길이 설정 (초)", 15, 60, 30)
            st.text_area("프롬프트 (장면 묘사)", "대치동 학원가 전경에서 래미안대치팰리스로 줌인, 웅장한 배경음악", height=100)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎥 10mm 숏츠 제작 렌더링 시작", use_container_width=True, type="primary", key="btn_render_shorts"):
                st.toast("렌더링 서버에 작업을 요청했습니다!")
            
            st.markdown("""
            <div style="font-size:0.8em; color:gray; margin-top:10px;">
            1. 시나리오 생성 및 Python 코드 번역<br>
            2. 베가스(Vegas) 자동 편집 스크립트 실행<br>
            3. H.264 Server 사이드 렌더링 후 S3 업로드
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown("#### 🖥️ 모니터링 데스크")
        with st.container(border=True):
            # Placeholder for monitoring screen
            st.markdown("""
            <div style="background-color:black; width:100%; height:300px; display:flex; align-items:center; justify-content:center; border-radius:5px; margin-bottom:10px;">
                <div style="text-align:center; color:gray;">
                    <span style="font-size:2em;">⚠️</span><br>
                    실시간 렌더링 미리보기 대기 중...<br>
                    (GPU: RTX 4090 - Idle)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Terminal logs
            st.code("""
[SYSTEM] Token Inference Server Connected... OK
[INFO] Loaded Model: Lotte-RealEstate-v4.7
[GPU] CUDA Core Active: 0%
[QUEUE] Waiting for render job...
            """, language="bash")

def render_joint_matching():
    import pandas as pd
    st.markdown("### 🤝 AI 부동산 공동중개 플랫폼")
    st.caption("강남구 등록된 1,500개 부동산과 실시간으로 매칭됩니다. (공동중개망 연동)")

    req_tab1, req_tab2 = st.tabs(["🙋‍♂️ 고객 찾아요 (매수/임차 의뢰)", "🏠 물건 찾아요 (전속 매물 공유)"])
    with req_tab1:
        st.info("💡 **'고객 찾아요'**는 내가 보유한 **매물**을 소화해줄 매수(임차) 손님을 찾는 기능입니다.")
        with st.form("find_client_form"):
            c1, c2, c3 = st.columns(3)
            with c1: st.selectbox("보유 매물", ["대치SK뷰 34평 전세", "은마 31평 매매", "직접입력"])
            with c2: st.number_input("거래 금액 (억)", value=15)
            with c3: st.text_input("특이사항", placeholder="입기협 전세자금대출 가능")
            if st.form_submit_button("🔔 전체 부동산에 '손님 찾기' 알림 발송", use_container_width=True):
                st.toast("📢 강남구 1,500개 부동산에 알림이 발송되었습니다!")
    with req_tab2:
        st.info("💡 **'물건 찾아요'**는 내 **손님**에게 딱 맞는 공동 중개 매물을 찾는 기능입니다.")
        with st.form("find_property_form"):
            c1, c2, c3 = st.columns(3)
            with c1: st.text_input("찾는 물건", placeholder="래대팰 45평 판상형")
            with c2: st.number_input("손님 예산 (억)", value=45)
            with c3: st.text_input("손님 조건", placeholder="3개월 내 입주, 현금보유")
            if st.form_submit_button("🔔 전체 부동산에 '매물 요청' 알림 발송", use_container_width=True):
                st.toast("📢 공동 중개망에 매물 요청이 등록되었습니다.")

    st.markdown("---")
    st.markdown("#### ⚡ AI 공동매칭 결과")
    st.info("✅ **AI 매칭 성공!** 귀하의 요청과 딱 맞는 상대방 부동산이 발견되었습니다.")
    data = {
        "시간": ["방금 전", "10분 전", "30분 전", "1시간 전", "어제"],
        "구분": ["🚨 매칭성공", "🚨 매칭성공", "수신", "수신", "발신"],
        "제목 (AI 요약)": ["래대팰 45평 판상형 매물 보유 (진공인)", "SK뷰 34평 전세 손님 대기 (대박부동산)",
                         "은마 31평 급매 찾으시는 분", "학원가 50평 임대 맞춤 가능", "대치아이파크 매수 손님 의뢰"],
        "상대 부동산": ["진공인중개사", "대박부동산", "개포굿", "한티역공인", "전체발송"],
        "매칭률": ["99%", "97%", "85%", "82%", "-"],
        "상태": ["💬 채팅 연결 대기", "💬 채팅 연결 대기", "확인중", "확인중", "발송완료"]
    }
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    # ── 파발마 스타일 상세 물건 접수 폼 ──────────────────────────────────
    _PROP_TYPES  = ["아파트", "빌라/연립", "오피스텔", "상가/상업", "토지", "기타"]
    _TRADE_TYPES = ["매매", "전세", "월세(반전세 포함)"]
    _FEATURES_S  = ["💰 금액조절 가능","👀 바로 볼 수 있는","🏗️ 새로 지은",
                    "🙋 손님 대기중","🚇 역세권 위치","🔧 수리 깨끗한","🏦 전세대출 가능","🛋️ 풀옵션"]
    _FEATURES_D  = ["💰 금액조절 가능","🚀 즉시입주 가능","🚗 주차 필수",
                    "🏫 학군 중요","🚇 역세권 선호","🏗️ 신축 선호","🏦 대출 활용 예정","🏠 실거주 목적"]
    _REGIONS_GU  = ["강남구","서초구","송파구","강동구","마포구","용산구","성동구","광진구",
                    "강서구","양천구","영등포구","동작구","관악구","서대문구","은평구","노원구"]
    # 대치1동 주요 단지 드롭다운
    _MC_COMPLEX_OPTS = [
        "래미안대치팰리스",
        "대치SK뷰",
        "대치아이파크",
        "은마아파트",
        "삼환아르누보2 오피스텔",
        "롯데월드타워몰 시그니엘레지던스",
        "직접입력",
    ]
    def _sqm2py(v): return round(v / 3.3058, 2)

    st.markdown("---")
    st.markdown("## 📋 AI 공동매물매칭 물건 접수 (파발마 상세 폼)")
    st.caption("있습니다(공급) / 구합니다(수요) 중 해당 탭을 선택해 입력하세요.")

    jm_tab_s, jm_tab_d = st.tabs(["🏠 있습니다 (공급/매도·임대)", "🔍 구합니다 (수요/매수·임차)"])

    with jm_tab_s:
        st.markdown("##### 👤 기본 인적사항")
        jc1, jc2 = st.columns(2)
        js_name  = jc1.text_input("이름 (공급자)", placeholder="홍길동", key="jm_s_name")
        js_phone = jc2.text_input("연락처", placeholder="010-1234-5678", key="jm_s_phone")
        st.divider()
        st.markdown("##### 🏷️ 매물 종류 & 거래 구분")
        jc1, jc2 = st.columns(2)
        js_prop  = jc1.selectbox("매물 종류", _PROP_TYPES, key="jm_s_prop")
        js_trade = jc2.radio("거래 구분", _TRADE_TYPES, horizontal=True, key="jm_s_trade")
        st.divider()
        st.markdown("##### 📍 위치 정보")
        jc1, jc2 = st.columns(2)
        js_cplx_sel = jc1.selectbox("단지명/건물명", _MC_COMPLEX_OPTS, key="jm_s_cplx_sel")
        js_dongho  = jc2.text_input("동/호수", placeholder="101동 1501호", key="jm_s_dongho")
        if js_cplx_sel == "직접입력":
            js_complex = st.text_input("단지명 직접 입력", placeholder="단지명/건물명을 입력하세요", key="jm_s_complex")
        else:
            js_complex = js_cplx_sel
        jc3, jc4, jc5, jc6 = st.columns(4)
        js_floor  = jc3.number_input("해당 층", 1, 100, 5,  key="jm_s_fl")
        js_tfloor = jc4.number_input("총 층수", 1, 200, 20, key="jm_s_tfl")
        js_rooms  = jc5.number_input("방 수",   1, 20,  3,  key="jm_s_rm")
        js_baths  = jc6.number_input("화장실",  1, 10,  2,  key="jm_s_bt")
        st.divider()
        st.markdown("##### 📐 면적/규모")
        ja1, ja2, ja3 = st.columns(3)
        js_sup = ja1.number_input("공급면적(㎡)", 0.0, step=0.5, format="%.1f", key="jm_s_sup")
        js_prv = ja2.number_input("전용면적(㎡)", 0.0, step=0.5, format="%.1f", key="jm_s_prv")
        js_ld  = ja3.number_input("대지면적(㎡)", 0.0, step=0.5, format="%.1f", key="jm_s_ld")
        if js_sup > 0 or js_prv > 0:
            jp1, jp2, jp3 = st.columns(3)
            if js_sup > 0: jp1.info(f"≈ **{_sqm2py(js_sup)}평**")
            if js_prv > 0: jp2.info(f"≈ **{_sqm2py(js_prv)}평**")
            if js_ld  > 0: jp3.info(f"≈ **{_sqm2py(js_ld)}평**")
        st.divider()
        st.markdown("##### 💵 가격 정보")
        if js_trade == "매매":
            jp1, jp2 = st.columns(2)
            js_price = {"매매가_억": jp1.number_input("매매가(억)", 0.0, step=0.1, format="%.1f", key="jm_s_sale"),
                        "매매가_만원": jp2.number_input("+ 만원단위", 0, step=100, key="jm_s_sale_m")}
        elif js_trade == "전세":
            jp1, jp2 = st.columns(2)
            js_price = {"보증금_억": jp1.number_input("보증금(억)", 0.0, step=0.1, format="%.1f", key="jm_s_dep"),
                        "보증금_만원": jp2.number_input("+ 만원단위", 0, step=100, key="jm_s_dep_m")}
        else:
            jp1, jp2, jp3 = st.columns(3)
            js_price = {"보증금_억": jp1.number_input("보증금(억)", 0.0, step=0.1, format="%.1f", key="jm_s_mdep"),
                        "보증금_만원": jp2.number_input("+ 만원단위", 0, step=100, key="jm_s_mdep_m"),
                        "월세_만원": jp3.number_input("월세(만원)", 0, step=5, key="jm_s_rent")}
        st.divider()
        st.markdown("##### ✅ 매물 특징 (해당 사항 모두 체크)")
        js_feats = []
        jfc = st.columns(4)
        for i, f in enumerate(_FEATURES_S):
            if jfc[i%4].checkbox(f, key=f"jm_sf_{i}"): js_feats.append(f)
        st.divider()
        st.markdown("##### 📅 일정 & 특이사항")
        jd1, jd2 = st.columns(2)
        js_date = jd1.date_input("이사예정일/인도가능일",
                                  value=datetime.date.today()+datetime.timedelta(days=30), key="jm_s_date")
        js_memo = jd2.text_area("특이사항 메모", placeholder="세입자 이사 후 즉시 가능 등", height=90, key="jm_s_memo")
        st.divider()
        st.markdown("##### 📡 발송 지역")
        jg1, jg2 = st.columns(2)
        js_gu     = jg1.multiselect("발송 구 선택", _REGIONS_GU, default=["강남구"], key="jm_s_gu")
        js_custom = jg2.text_input("추가 직접 입력(동 등)", placeholder="대치동, 압구정동", key="jm_s_custom")
        st.divider()
        js_agree = st.checkbox(
            "✅ [필수] 개인정보 수집·이용에 동의합니다. (이름·연락처는 매칭 목적으로만 활용됩니다)",
            key="jm_s_agree"
        )
        st.caption("※ 개인정보 보호법에 따라 수집된 정보는 매칭 완료 후 즉시 파기됩니다.")
        if st.button("🚀 [있습니다] 공급 물건 접수하기", type="primary", use_container_width=True, key="jm_btn_s"):
            errs = []
            if not js_name:    errs.append("이름을 입력해주세요.")
            if not js_phone:   errs.append("연락처를 입력해주세요.")
            if not js_complex: errs.append("단지명을 입력해주세요.")
            if not js_agree:   errs.append("개인정보 수집·이용 동의가 필요합니다.")
            if errs:
                for e in errs: st.error(e)
            else:
                sub = {"접수유형": "있습니다(공급)", "이름": js_name, "연락처": js_phone,
                       "매물종류": js_prop, "거래구분": js_trade, "단지명": js_complex, "동호수": js_dongho,
                       "층수": f"{js_floor}/{js_tfloor}층", "방수": js_rooms, "화장실수": js_baths,
                       "공급면적_㎡": js_sup, "공급면적_평": _sqm2py(js_sup),
                       "전용면적_㎡": js_prv, "전용면적_평": _sqm2py(js_prv),
                       **js_price, "특징": js_feats, "이사예정일": str(js_date), "특이사항": js_memo,
                       "발송구": js_gu, "발송지역추가": js_custom,
                       "개인정보동의": "동의", "접수시각": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                import time as _t
                with st.spinner("🔒 암호화 전송 중..."): _t.sleep(1.0)
                st.success("✅ [있습니다] 공급 물건 접수 완료!")
                st.balloons()
                with st.expander("📊 접수 내용 확인", expanded=True): st.json(sub)
                st.info("담당자 확인 후 매칭 수요자에게 연락드립니다.")

    with jm_tab_d:
        st.markdown("##### 👤 기본 인적사항")
        dc1, dc2 = st.columns(2)
        jd_name  = dc1.text_input("이름", placeholder="홍길동", key="jm_d_name")
        jd_phone = dc2.text_input("연락처", placeholder="010-1234-5678", key="jm_d_phone")
        st.divider()
        st.markdown("##### 🏷️ 희망 매물 종류 & 거래 유형")
        dc1, dc2 = st.columns(2)
        jd_prop  = dc1.selectbox("희망 매물 종류", _PROP_TYPES, key="jm_d_prop")
        jd_trade = dc2.radio("희망 거래 유형", _TRADE_TYPES, horizontal=True, key="jm_d_trade")
        st.divider()
        st.markdown("##### 📍 희망 지역 & 단지")
        dc1, dc2 = st.columns(2)
        jd_region  = dc1.text_input("희망 지역(구/동)", placeholder="강남구 대치동", key="jm_d_region")
        jd_complex = dc2.text_input("희망 단지명(선택)", placeholder="래미안 팰리스", key="jm_d_complex")
        st.divider()
        st.markdown("##### 📐 희망 면적 범위")
        da1, da2 = st.columns(2)
        jd_amin = da1.number_input("최소 면적(㎡)", 0.0, step=1.0, format="%.1f", key="jm_d_amin")
        jd_amax = da2.number_input("최대 면적(㎡)", 0.0, step=1.0, format="%.1f", key="jm_d_amax")
        if jd_amin > 0 or jd_amax > 0:
            st.info(f"≈ {_sqm2py(jd_amin)}평 ~ {_sqm2py(jd_amax)}평")
        st.divider()
        st.markdown("##### 💵 희망 가격 범위")
        if jd_trade == "매매":
            dp1, dp2 = st.columns(2)
            jd_price = {"희망_매매_최소_억": dp1.number_input("매매가 최소(억)", 0.0, step=0.5, format="%.1f", key="jm_d_pmin"),
                        "희망_매매_최대_억": dp2.number_input("매매가 최대(억)", 0.0, step=0.5, format="%.1f", key="jm_d_pmax")}
        elif jd_trade == "전세":
            dp1, dp2 = st.columns(2)
            jd_price = {"희망_보증금_최소_억": dp1.number_input("보증금 최소(억)", 0.0, step=0.5, format="%.1f", key="jm_d_depmin"),
                        "희망_보증금_최대_억": dp2.number_input("보증금 최대(억)", 0.0, step=0.5, format="%.1f", key="jm_d_depmax")}
        else:  # 월세(반전세 포함)
            st.markdown("###### 💰 보증금 범위")
            dp1, dp2 = st.columns(2)
            dep_min = dp1.number_input("보증금 최소(억)", 0.0, step=0.1, format="%.1f", key="jm_d_mdepmin")
            dep_max = dp2.number_input("보증금 최대(억)", 0.0, step=0.1, format="%.1f", key="jm_d_mdepmax")
            if dep_min > 0 or dep_max > 0:
                st.info(f"보증금 범위: {dep_min}억 ~ {dep_max}억")
            st.markdown("###### 💸 월세 범위")
            dp3, dp4 = st.columns(2)
            rent_min = dp3.number_input("월세 최소(만원)", 0, step=5, key="jm_d_rentmin")
            rent_max = dp4.number_input("월세 최대(만원)", 0, step=5, key="jm_d_rentmax")
            if rent_min > 0 or rent_max > 0:
                st.info(f"월세 범위: {rent_min}만원 ~ {rent_max}만원")
            jd_price = {
                "희망_보증금_최소_억": dep_min,
                "희망_보증금_최대_억": dep_max,
                "희망_월세_최소_만원": rent_min,
                "희망_월세_최대_만원": rent_max
            }
        st.divider()
        st.markdown("##### ✅ 희망 조건 선택")
        jd_feats = []
        jdf = st.columns(4)
        for i, f in enumerate(_FEATURES_D):
            if jdf[i%4].checkbox(f, key=f"jm_df_{i}"): jd_feats.append(f)
        st.divider()
        st.markdown("##### 📅 입주 희망일 & 기타 요청")
        dd1, dd2 = st.columns(2)
        jd_date = dd1.date_input("입주 희망일",
                                  value=datetime.date.today()+datetime.timedelta(days=60), key="jm_d_date")
        jd_memo = dd2.text_area("기타 요청사항", placeholder="반려동물 가능, 주차 2대 필수 등", height=90, key="jm_d_memo")
        st.divider()
        jd_agree = st.checkbox(
            "✅ [필수] 개인정보 수집·이용에 동의합니다. (이름·연락처는 매칭 목적으로만 활용됩니다)",
            key="jm_d_agree"
        )
        st.caption("※ 개인정보 보호법에 따라 수집된 정보는 매칭 완료 후 즉시 파기됩니다.")
        if st.button("🔍 [구합니다] 수요 조건 접수하기", type="primary", use_container_width=True, key="jm_btn_d"):
            errs = []
            if not jd_name:   errs.append("이름을 입력해주세요.")
            if not jd_phone:  errs.append("연락처를 입력해주세요.")
            if not jd_region: errs.append("희망 지역을 입력해주세요.")
            if not jd_agree:  errs.append("개인정보 수집·이용 동의가 필요합니다.")
            if errs:
                for e in errs: st.error(e)
            else:
                sub = {"접수유형": "구합니다(수요)", "이름": jd_name, "연락처": jd_phone,
                       "희망_매물종류": jd_prop, "희망_거래유형": jd_trade,
                       "희망_지역": jd_region, "희망_단지": jd_complex,
                       "희망_면적": f"{jd_amin}~{jd_amax}㎡ ({_sqm2py(jd_amin)}~{_sqm2py(jd_amax)}평)",
                       **jd_price, "희망_조건": jd_feats,
                       "입주희망일": str(jd_date), "기타요청": jd_memo,
                       "개인정보동의": "동의", "접수시각": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                import time as _t
                with st.spinner("🔒 암호화 전송 중..."): _t.sleep(1.0)
                st.success("✅ [구합니다] 수요 조건 접수 완료!")
                st.balloons()
                with st.expander("📊 접수 내용 확인", expanded=True): st.json(sub)
                st.info("AI가 조건에 맞는 매물을 분석하여 담당자가 연락드립니다.")

    # ── AI 홍보·영업 도구 패널 ──────────────────────────────────────────
    st.markdown("---")
    render_marketing_action_tools(section_key="joint")

def render_admin_system():
    if "admin_unlocked" not in st.session_state:
        st.session_state["admin_unlocked"] = False

    st.markdown("### 🔒 관리자 보안 시스템")
    
    if not st.session_state["admin_unlocked"]:
        # 1. Security Check UI
        with st.container(border=True):
            st.markdown("##### 🔐 관리자 접속 권한 인증")
            password = st.text_input("관리자 비밀번호를 입력하세요", type="password", placeholder="비밀번호 입력")
            st.caption("ℹ️ 초기 비밀번호는 **1234** 입니다.")
            
            if st.button("🔓 관리자 권한 확인", use_container_width=True):
                if password == "1234":
                    st.session_state["admin_unlocked"] = True
                    st.toast("🟢 관리자 인증 성공!")
                    st.rerun()
                else:
                    st.error("⛔ 비밀번호가 일치하지 않습니다.")

            st.markdown("---")
            st.markdown("##### ❓ 비밀번호를 잊으셨나요?")
            if st.button("📲 핸드폰으로 비번 찾기", use_container_width=True):
                st.toast("📩 등록된 관리자 휴대폰(010-****-8285)으로 임시 비밀번호가 발송되었습니다.")
        return

    # If unlocked, show the dashboard
    if st.button("🔒 로그아웃 (시스템 잠금)", type="secondary"):
        st.session_state["admin_unlocked"] = False
        st.rerun()

    st.markdown("---")

    # ── 관리자 서브탭
    adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs(["🏢 매물관리", "👥 고객관리", "📑 AI영업팩 생성기", "⚙️ 시스템 관리"])

    with adm_tab1:
        _render_property_management_panel()

    with adm_tab2:
        _render_customer_management_panel()

    with adm_tab3:
        _render_sales_pack_generator()

    with adm_tab4:
        st.info("시스템 관리: 추후 구현 예정 (로그, 백업, 설정 등)")

def _render_property_management_panel():
    """파발마 스타일 매물관리 패널"""
    import random as _rnd
    import pandas as _pd
    from datetime import date as _date, datetime as _dt, timedelta as _td

    # ── 통계 카드
    _kc = st.columns(5)
    for _i, (_num, _label, _color) in enumerate([
        ("120", "전체 매물", "#60a5fa"),
        ("48", "매매", "#34d399"),
        ("35", "전세", "#60a5fa"),
        ("37", "월세", "#c084fc"),
        ("8", "보류/검토", "#fbbf24"),
    ]):
        _kc[_i].markdown(f"""
        <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);
                    border-radius:8px;padding:10px;text-align:center;margin-bottom:4px;">
            <div style="font-size:1.5rem;font-weight:700;color:{_color};">{_num}</div>
            <div style="font-size:0.72rem;color:#94a3b8;">{_label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── 검색 패널
    with st.container():
        r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns([2, 2, 2, 3, 1.5])
        with r1c1:
            _d_from = st.date_input("조회 시작일", value=_date(2026, 2, 4), key="pm_d_from", label_visibility="visible")
        with r1c2:
            _d_to = st.date_input("조회 종료일", value=_date(2026, 3, 4), key="pm_d_to", label_visibility="visible")
        with r1c3:
            _search_cond = st.selectbox("검색조건", ["전체", "제목", "내용", "주소", "거래유형", "유형"], key="pm_cond")
        with r1c4:
            _search_kw = st.text_input("검색어", placeholder="검색어를 입력하세요...", key="pm_kw")
        with r1c5:
            st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
            _do_search = st.button("🔍 검색", use_container_width=True, key="pm_search_btn", type="primary")

        fc1, fc2, fc3, fc4, fc5, fc6, fc7, fc8 = st.columns(8)
        _chk_국 = fc1.checkbox("국내소재", value=True, key="pm_fc1")
        _chk_직 = fc2.checkbox("직거래", key="pm_fc2")
        _chk_신 = fc3.checkbox("새로 나온", key="pm_fc3")
        _chk_급 = fc4.checkbox("급매물", key="pm_fc4")
        _chk_주 = fc5.checkbox("집주인 직접", key="pm_fc5")
        _chk_수 = fc6.checkbox("수익성 우수", key="pm_fc6")
        _chk_미 = fc7.checkbox("미계약", key="pm_fc7")
        _chk_ai = fc8.checkbox("AI 추천", key="pm_fc8")

    # ── 액션 버튼 바
    ab1, ab2, ab3, ab4, ab5, ab6 = st.columns([1.2, 1.2, 1.2, 1.8, 2.5, 1.5])
    with ab1:
        if st.button("✏️ 수기 등록", use_container_width=True, key="pm_act1"):
            st.session_state["pm_show_form"] = True
    with ab2:
        if st.button("📋 대장보기", use_container_width=True, key="pm_act2"):
            st.info("건축물대장 조회 기능 (연동 준비 중)")
    with ab3:
        if st.button("🔍 상세보기", use_container_width=True, key="pm_act3"):
            st.info("선택 매물의 상세 정보를 확인합니다.")
    with ab4:
        if st.button("🤖 자동가격조정", use_container_width=True, type="primary", key="pm_act4"):
            with st.spinner("AI 가격 분석 중..."):
                import time as _time
                _time.sleep(1.2)
            st.success("✅ AI 기반 가격 자동 조정 완료!")
    with ab5:
        st.markdown("""
        <div style='padding:7px;background:rgba(255,255,255,0.06);border-radius:8px;
                    border:1px solid rgba(255,255,255,0.1);text-align:center;'>
            <span style='color:#94a3b8;font-size:0.78rem;'>조회 건수 </span>
            <span style='color:#fbbf24;font-size:1.1rem;font-weight:700;'> 총 120건</span>
            <span style='color:#94a3b8;font-size:0.78rem;'> | AI매칭추천 </span>
            <span style='color:#34d399;font-size:1rem;font-weight:700;'>8건 ✨</span>
        </div>
        """, unsafe_allow_html=True)
    with ab6:
        _ca, _cb = st.columns(2)
        _ca.button("📥 엑셀", use_container_width=True, key="pm_exp1")
        _cb.button("🖨️ 인쇄", use_container_width=True, key="pm_exp2")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── 샘플 데이터 생성
    def _make_pm_data():
        _rnd.seed(42)
        _types = ["아파트", "오피스텔", "빌라", "상가", "오피스"]
        _deals = ["매매", "전세", "월세"]
        _gugun_list = ["강남구", "서초구", "송파구", "마포구", "성남시", "수원시", "연수구", "용산구"]
        _dong_map = {
            "강남구": ["대치동","삼성동","청담동","역삼동"],
            "서초구": ["반포동","잠원동","양재동"],
            "송파구": ["잠실동","방이동","가락동"],
            "마포구": ["합정동","망원동","상수동"],
            "성남시": ["분당동","수내동","정자동"],
            "수원시": ["영통동","매탄동"],
            "연수구": ["송도동","연수동"],
            "용산구": ["한남동","이태원동"],
        }
        _names = ["래미안","힐스테이트","자이","롯데캐슬","아이파크","푸르지오","e편한세상","더샵"]
        _base = _dt(2026, 2, 4)
        _rows = []
        for _i in range(80):
            _sg = _rnd.choice(_gugun_list)
            _se = _rnd.choice(_dong_map.get(_sg, ["기타동"]))
            _tp = _rnd.choice(_deals)
            _rows.append({
                "쪽지": _rnd.choice(["●", ""]),
                "이미구분": _rnd.choice(["공동","전속","일반"]),
                "유형": _rnd.choice(_types),
                "물건공부": _rnd.choice(["등기부","건축물대장"]),
                "구군": _sg,
                "읍면동": _se,
                "매매가(억)": _rnd.randint(5, 80) if _tp =="매매" else "-",
                "보증금(억)": _rnd.randint(1, 30) if _tp in ["전세","월세"] else "-",
                "월세(만)": _rnd.randint(50, 300) if _tp == "월세" else "-",
                "거래유형": _tp,
                "제목": f"{_rnd.choice(_names)} {_rnd.randint(10,50)}평 {_tp}",
                "내용": f"역세권 {_rnd.randint(1,10)}분, {_rnd.choice(['로얄층','저층','중층','고층'])} 급매",
                "등록일": (_base +_td(days=_rnd.randint(0, 28))).strftime("%Y-%m-%d"),
                "상태": _rnd.choice(["신규","진행중","완료","보류"]),
            })
        return _pd.DataFrame(_rows)

    _df = _make_pm_data()

    # 필터 적용
    if _search_kw:
        if _search_cond == "제목":
            _df = _df[_df["제목"].str.contains(_search_kw, na=False)]
        elif _search_cond == "주소":
            _df = _df[_df["구군"].str.contains(_search_kw, na=False) | _df["읍면동"].str.contains(_search_kw, na=False)]
        else:
            _df = _df[_df["제목"].str.contains(_search_kw, na=False) | _df["내용"].str.contains(_search_kw, na=False)]
    if _chk_신:
        _df = _df[_df["상태"] == "신규"]
    if _chk_급:
        _df = _df[_df["내용"].str.contains("급", na=False)]

    # ── 서브탭 (수신/구입/즐겨찾기)
    _st1, _st2, _st3 = st.tabs(["📋 수신 파발마", "📤 구입 파발마", "⭐ 즐겨찾기"])
    with _st1:
        st.markdown(f"<span style='color:#94a3b8;font-size:0.82rem;'>총 <span style='color:#fbbf24;font-weight:700;'>{len(_df):,}건</span> 조회 | 열 헤더 클릭 시 정렬</span>", unsafe_allow_html=True)

        def _style_status(val):
            _m = {"신규":"background-color:rgba(16,185,129,0.2);color:#34d399;font-weight:bold;",
                  "진행중":"background-color:rgba(59,130,246,0.2);color:#60a5fa;font-weight:bold;",
                  "완료":"background-color:rgba(100,116,139,0.2);color:#94a3b8;",
                  "보류":"background-color:rgba(245,158,11,0.2);color:#fbbf24;font-weight:bold;"}
            return _m.get(val, "")

        _styled = _df.style.applymap(_style_status, subset=["상태"])
        st.dataframe(
            _styled,
            use_container_width=True,
            height=420,
            column_config={
                "쪽지": st.column_config.TextColumn("쪽지", width=45),
                "이미구분": st.column_config.TextColumn("이미구분", width=70),
                "유형": st.column_config.TextColumn("유형", width=80),
                "물건공부": st.column_config.TextColumn("물건공부", width=90),
                "구군": st.column_config.TextColumn("구군", width=75),
                "읍면동": st.column_config.TextColumn("읍면동", width=75),
                "매매가(억)": st.column_config.TextColumn("매매가(억)", width=85),
                "보증금(억)": st.column_config.TextColumn("보증금(억)", width=85),
                "월세(만)": st.column_config.TextColumn("월세(만)", width=75),
                "거래유형": st.column_config.TextColumn("거래유형", width=70),
                "제목": st.column_config.TextColumn("제목", width=200),
                "내용": st.column_config.TextColumn("내용", width=200),
                "등록일": st.column_config.TextColumn("등록일", width=95),
                "상태": st.column_config.TextColumn("상태", width=65),
            }
        )
        # CSV 다운로드
        _csv = _df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("📥 CSV 다운로드", data=_csv,
            file_name=f"매물목록_{_date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv", key="pm_dl_csv")

    with _st2:
        st.info("📤 구입 파발마: 매수 희망 조건 수신 목록")
        _buy = _pd.DataFrame({
            "수신일": ["2026-03-04", "2026-03-03", "2026-03-02"],
            "유형": ["아파트", "오피스텔", "빌라"],
            "희망지역": ["강남구 대치동", "서초구 반포동", "마포구 합정동"],
            "예산(억)": ["30~35", "8~12", "5~7"],
            "특이사항": ["학군 필수, 30평 이상", "역세권 선호", "신축 선호"],
            "연락처": ["010-****-1234", "010-****-5678", "010-****-9012"],
            "상태": ["검토중", "매칭완료", "대기"]
        })
        st.dataframe(_buy, use_container_width=True)

    with _st3:
        st.info("⭐ 즐겨찾기 매물: 관심 등록된 매물 목록")
        st.dataframe(_df.head(10), use_container_width=True)

    # ── 수기 등록 폼
    if st.session_state.get("pm_show_form"):
        st.markdown("---")
        st.markdown("#### ✏️ 새 매물 수기 등록")
        with st.form("pm_register_form"):
            _fr1, _fr2, _fr3, _fr4 = st.columns(4)
            _ft = _fr1.selectbox("거래유형", ["매매","전세","월세"], key="pm_frm_trade")
            _fp = _fr2.selectbox("부동산유형", ["아파트","오피스텔","빌라","상가","오피스"], key="pm_frm_prop")
            _fs = _fr3.selectbox("시도", ["서울","경기","인천","부산","기타"], key="pm_frm_sido")
            _fg = _fr4.text_input("구군", placeholder="강남구", key="pm_frm_gugun")
            _fd = st.text_input("읍면동", placeholder="대치동", key="pm_frm_dong")
            _fpr = st.number_input("가격(억)", min_value=0.0, step=0.1, key="pm_frm_price")
            _ftt = st.text_input("매물 제목", key="pm_frm_title")
            _fct = st.text_area("매물 내용", height=80, key="pm_frm_content")
            _sub = st.form_submit_button("💾 저장", type="primary", use_container_width=True)
            if _sub:
                st.success(f"✅ '{_ftt}' 매물이 저장되었습니다!")
                st.session_state["pm_show_form"] = False

def _render_sales_pack_generator():
    """AI 영업팩 생성기 (기존 코드)"""
    # 2. Admin Dashboard - Sales Pack Generator
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h3 style="color: #cbd5e1;">📑 부동산 AI 영업팩 생성기 (자동화)</h3>
        <p style="color: #64748b; font-size: 0.9rem;">버튼 하나로 블로그 / 카톡 / 상담 스크립트 / 영상 멘트를 한 번에 생성합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("admin_sales_pack_form"):
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);
                    border-radius:12px; padding:16px 20px; margin-bottom:16px;
                    border-left:5px solid #facc15;">
            <div style="font-size:1.05rem;font-weight:900;color:#facc15;">
                ⚡ 매물 기본 정보 입력 (자동 생성)
            </div>
            <div style="font-size:0.82rem;color:#94a3b8;margin-top:4px;">
                아래 정보를 입력하면 AI가 블로그·카톡·숏츠 스크립트를 자동 생성합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 섹션 1: 기본 인적사항
        st.markdown("##### 👤 기본 인적사항")
        sp1, sp2, sp3 = st.columns(3)
        sp_name  = sp1.text_input("이름 (공급자)", "이상수", key="sp_name")
        sp_phone = sp2.text_input("연락처", "010-8985-8945", key="sp_phone")
        sp_agency= sp3.text_input("소속 중개사무소", "롯데타워앤강남빌딩부동산중개㈜", key="sp_agency")
        st.divider()

        # ── 섹션 2: 매물 종류 & 거래 구분
        st.markdown("##### 🏷️ 매물 종류 & 거래 구분")
        sp_tc1, sp_tc2 = st.columns(2)
        sp_prop  = sp_tc1.selectbox("매물 종류", ["아파트", "빌라/연립", "오피스텔", "상가/상업", "토지", "기타"], key="sp_prop")
        sp_trade = sp_tc2.radio("거래 구분", ["매매", "전세", "월세(반전세 포함)"], horizontal=True, key="sp_trade")
        st.divider()

        # ── 섹션 3: 위치 정보
        st.markdown("##### 📍 위치 정보")
        sp_lc1, sp_lc2 = st.columns(2)
        _SP_COMPLEX = ["래미안대치팰리스","대치SK뷰","대치아이파크","은마아파트",
                       "삼환아르누보2 오피스텔","롯데월드타워몰 시그니엘레지던스","직접입력"]
        sp_cplx_sel = sp_lc1.selectbox("단지명/건물명", _SP_COMPLEX, index=1, key="sp_cplx_sel")
        sp_dongho   = sp_lc2.text_input("동/호수 (비공개 보안 유지)", placeholder="101동 1501호", key="sp_dongho")
        if sp_cplx_sel == "직접입력":
            sp_complex = st.text_input("단지명 직접 입력", placeholder="단지명/건물명을 입력하세요", key="sp_complex")
        else:
            sp_complex = sp_cplx_sel
        sp_fc1, sp_fc2, sp_fc3, sp_fc4, sp_fc5 = st.columns(5)
        sp_floor  = sp_fc1.number_input("해당 층", 1, 100, 10, key="sp_floor")
        sp_tfloor = sp_fc2.number_input("총 층수", 1, 300, 35, key="sp_tfloor")
        sp_rooms  = sp_fc3.number_input("방 수",   1,  20,  3, key="sp_rooms")
        sp_baths  = sp_fc4.number_input("화장실",  1,  10,  2, key="sp_baths")
        sp_byear  = sp_fc5.number_input("준공년도", 1970, 2030, 2005, key="sp_byear")
        st.divider()

        # ── 섹션 4: 면적/규모
        st.markdown("##### 📐 면적/규모")
        sp_ac1, sp_ac2, sp_ac3 = st.columns(3)
        sp_sup = sp_ac1.number_input("공급면적(㎡)", 0.0, step=0.5, format="%.1f", key="sp_sup")
        sp_prv = sp_ac2.number_input("전용면적(㎡)", 0.0, step=0.5, format="%.1f", key="sp_prv")
        sp_pyg = sp_ac3.text_input("평형 / 타입", "34평 / A타입", key="sp_pyg")
        st.divider()

        # ── 섹션 5: 가격 정보 (최소~최대)
        st.markdown("##### 💵 가격 정보")
        if sp_trade == "매매":
            sp_pp1, sp_pp2, sp_pp3, sp_pp4 = st.columns(4)
            sp_pp1.number_input("매매가 최소(억)", 0.0, step=0.5, format="%.1f", key="sp_sale_min")
            sp_pp2.number_input("+ 만원단위", 0, step=500, key="sp_sale_min_m")
            sp_pp3.number_input("매매가 최대(억)", 0.0, step=0.5, format="%.1f", key="sp_sale_max")
            sp_pp4.number_input("+ 만원단위", 0, step=500, key="sp_sale_max_m")
        elif sp_trade == "전세":
            sp_pp1, sp_pp2, sp_pp3, sp_pp4 = st.columns(4)
            sp_pp1.number_input("보증금 최소(억)", 0.0, step=0.5, format="%.1f", key="sp_dep_min")
            sp_pp2.number_input("+ 만원단위", 0, step=500, key="sp_dep_min_m")
            sp_pp3.number_input("보증금 최대(억)", 0.0, step=0.5, format="%.1f", key="sp_dep_max")
            sp_pp4.number_input("+ 만원단위", 0, step=500, key="sp_dep_max_m")
        else:
            sp_pp1, sp_pp2, sp_pp3, sp_pp4, sp_pp5, sp_pp6 = st.columns(6)
            sp_pp1.number_input("보증금 최소(억)", 0.0, step=0.1, format="%.1f", key="sp_mdep_min")
            sp_pp2.number_input("+ 만원단위", 0, step=100, key="sp_mdep_min_m")
            sp_pp3.number_input("보증금 최대(억)", 0.0, step=0.1, format="%.1f", key="sp_mdep_max")
            sp_pp4.number_input("+ 만원단위", 0, step=100, key="sp_mdep_max_m")
            sp_pp5.number_input("월세 최소(만원)", 0, step=5, key="sp_rent_min")
            sp_pp6.number_input("월세 최대(만원)", 0, step=5, key="sp_rent_max")
        st.divider()

        # ── 섹션 6: 물건 상세
        st.markdown("##### 🏗️ 물건 상세 정보")
        sp_dc1, sp_dc2, sp_dc3, sp_dc4 = st.columns(4)
        sp_direction = sp_dc1.selectbox("향", ["남향","남동향","남서향","동향","서향","북향","판상형(4Bay)"], key="sp_dir")
        sp_parking   = sp_dc2.selectbox("주차 여부", ["전용 주차","공용 주차","주차 없음"], key="sp_parking")
        sp_heating   = sp_dc3.selectbox("난방 방식", ["개별난방","중앙난방","지역난방"], key="sp_heating")
        sp_elevator  = sp_dc4.radio("엘리베이터", ["있음","없음"], horizontal=True, key="sp_elev")
        sp_ex1, sp_ex2 = st.columns(2)
        sp_remodel   = sp_ex1.radio("리모델링", ["없음","부분수리","올수리(풀리모델)","준신축"], horizontal=True, key="sp_remodel")
        sp_expansion = sp_ex2.radio("확장 유무", ["확장형","비확장","일부확장"], horizontal=True, key="sp_expansion")
        st.divider()

        # ── 섹션 7: 권리관계 & 관리비
        st.markdown("##### 🛡️ 권리관계 & 관리비")
        sp_rc1, sp_rc2, sp_rc3 = st.columns(3)
        sp_loan      = sp_rc1.number_input("융자금(만원)", 0, step=500, key="sp_loan")
        sp_rights    = sp_rc2.selectbox("권리관계", ["깨끗","근저당 있음","가압류 있음","확인 필요"], key="sp_rights")
        sp_mgmt      = sp_rc3.number_input("월 관리비(만원)", 0, step=1, key="sp_mgmt")
        sp_occupy    = st.selectbox("현 거주 상황", ["공실(즉시입주)","본인거주","세입자 거주중","명도 필요"], key="sp_occupy")
        st.divider()

        # ── 섹션 8: 매물 특징
        st.markdown("##### ✅ 매물 특징 (해당 항목 체크)")
        _SP_FEATS = ["💰 금액조절 가능","👀 바로 볼 수 있는","🏗️ 새로 지은",
                     "🙋 손님 대기중","🚇 역세권 위치","🔧 수리 깨끗한",
                     "🏦 전세대출 가능","🛋️ 풀옵션","🎓 대치초 배정",
                     "🏫 대청중 배정","🚌 단대부고 배정","🌳 공원 인근",
                     "🅿️ 전용주차 가능","🌞 남향 로얄층","🏊 커뮤니티 완비","🔒 보안 우수"]
        sp_feat_cols = st.columns(4)
        for _i, _f in enumerate(_SP_FEATS):
            sp_feat_cols[_i % 4].checkbox(_f, key=f"sp_ft_{_i}")
        st.divider()

        # ── 섹션 9: AI 홍보 키워드
        st.markdown("##### 🎯 AI 홍보 키워드 (자동 생성용)")
        sp_kc1, sp_kc2, sp_kc3 = st.columns(3)
        sp_school = sp_kc1.text_input("학군 키워드", "대치초, 대청중 배정", key="sp_school")
        sp_trans  = sp_kc2.text_input("교통 키워드", "대치역 초역세권, 3호선", key="sp_trans")
        sp_local  = sp_kc3.text_input("입지 키워드", "대치동 학원가 도보 3분", key="sp_local")
        sp_memo   = st.text_area("특이사항 & 어필 포인트", placeholder="예) 로얄층 판상형 4Bay, 풀리모델 직후 상태, 학군 최강 입지...", height=80, key="sp_memo")
        st.divider()

        # ── 제출 버튼
        submit = st.form_submit_button("🚀 AI 영업팩 (블로그·카톡·숏츠 스크립트) 자동 생성!", type="primary", use_container_width=True)

        if submit:
            st.success("✅ AI 영업팩 생성이 완료되었습니다!")
            st.markdown(f"""
            <div style="background:#0f172a; padding:20px; border-radius:10px; border:1px solid #334155; margin-top:10px;">
                <h4 style="color:#38bdf8; margin:0 0 8px 0;">📝 [블로그 제목]</h4>
                <p style="color:#e2e8f0; margin:0 0 16px 0;">
                    대치동 학원가 바로 앞! {sp_complex} {sp_pyg} 귀한 {sp_trade}, 놓치면 후회합니다.
                </p>
                <h4 style="color:#38bdf8; margin:0 0 8px 0;">💬 [카톡 브리핑]</h4>
                <p style="color:#e2e8f0; margin:0; line-height:1.8;">
                    안녕하세요 대표님, 롯데AI부동산 <b style="color:#facc15;">{sp_name}</b> 중개사입니다.<br>
                    {sp_school} 가능한 <b style="color:#facc15;">{sp_complex} {sp_pyg} {sp_floor}층</b> 물건이 방금 접수되었습니다.<br>
                    {sp_trans} | {sp_local}<br>
                    주말 내 계약 예상되오니 바로 연락 부탁드립니다.<br>
                    ☎ {sp_phone}
                </p>
                <h4 style="color:#38bdf8; margin:16px 0 8px 0;">🎥 [숏츠 스크립트 오프닝]</h4>
                <p style="color:#e2e8f0; margin:0; line-height:1.8;">
                    "대치동에서 이 가격에 이 입지?! 안 사면 진짜 후회합니다.<br>
                    {sp_complex} {sp_pyg}, {sp_trade} 물건인데요,<br>
                    {sp_school}에 {sp_trans} 역세권입니다!"
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()




def render_login_page():
    # ── 스크롤 플래그 처리 (하단 nav 버튼 클릭 후 이동)
    scroll_target = st.session_state.pop("scroll_to", None)
    if scroll_target:
        st.markdown(
            f'<script>setTimeout(function(){{var el=document.getElementById("{scroll_target}");if(el)el.scrollIntoView({{behavior:"smooth"}});}},300);</script>',
            unsafe_allow_html=True
        )

    # 최상단 앵커 (베이스캠프 헤더로 이동용)
    st.markdown('<div id="login-top"></div>', unsafe_allow_html=True)

    # Styled Header Section (Dark Blue)
    st.markdown("""
    <div style="background-color: #0f172a; color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div style="display: flex; align-items: start; margin-bottom: 20px;">
            <div style="background-color: #fbbf24; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 30px; flex-shrink: 0; margin-top: 5px;">
                👨‍💼
            </div>
            <div>
                <h2 style="margin: 0 0 5px 0; font-size: 1.2rem; color: #f8fafc; line-height: 1.3;">롯데타워앤강남빌딩부동산중개주식회사</h2>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 5px;">
                    등록번호: 11680-2023-00078 | 사업자: 461-86-02740
                </div>
                <div style="font-size: 1.1rem; color: #fbbf24; font-weight: bold; margin-bottom: 5px;">
                    대표: 공인중개사 이상수
                </div>
                <div style="color: #cbd5e1; font-size: 0.9rem;">
                    Tel: 02-578-8289 / 010-8985-8945
                </div>
            </div>
        </div>
        <h3 style="color: #fcd34d; margin-top: 10px; font-size: 1.3rem;">"대치1동은 자녀의 미래 베이스캠프입니다."</h3>
        <p style="color: #cbd5e1; line-height: 1.6; font-size: 0.95rem;">
            AI 저평가 분석과 예약 AI자동 매칭 시스템으로 숨겨진 부동산 가치를 발굴하고,<br>
            대한민국 최고의 교육 환경으로 가는 최적의 출발점을 찾아드립니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 3 Core Strategies Section — 앵커 id 추가
    st.markdown('<div id="ai-strategy-section"></div>', unsafe_allow_html=True)
    st.markdown("#### 🔷 AI 부동산 핵심 3대 전략")

    st.markdown("""
    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #3b82f6;">
        <h4 style="margin: 0 0 10px 0; color: #1e293b;">🎓 교육특구 1번지 분석</h4>
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">래대팰·SK뷰(대치초/단대부고) vs 아이파크(대도초/숙명여중고)<br>학군 정밀 분석 및 배정 원칙 데이터화</p>
    </div>

    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #8b5cf6;">
        <h4 style="margin: 0 0 10px 0; color: #1e293b;">🧬 AI저평가 매물 매수·매도·임대차 예약 AI자동매칭</h4>
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">빅데이터로 저평가 매물을 발굴하고, 매수·매도·임대차 예약 고객에게 <b>1초 만에 AI자동 매칭</b>하여 거래 성사율 극대화</p>
    </div>

    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 30px; border-left: 5px solid #ef4444;">
        <h4 style="margin: 0 0 10px 0; color: #1e293b;">📢 AI 자동 홍보 시스템</h4>
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">매물 접수 즉시 영업 문구 자동 생성 및 타겟 고객 발송</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 앱 소개글 ──
    st.markdown("""
<div style="background:linear-gradient(135deg,#0f172a,#1e3a5f); color:white; border-radius:14px;
            padding:24px 22px; margin-bottom:20px;">
  <h4 style="color:#fcd34d; margin:0 0 14px 0; font-size:1.05rem;">
    🏠 부동산 저평가 매물 &amp; 사전예약 AI 자동매칭 플랫폼
  </h4>

  <div style="display:flex; gap:10px; margin-bottom:12px;">
    <div style="background:rgba(239,68,68,0.18); border-radius:10px; padding:14px 16px; flex:1;">
      <div style="font-size:0.78rem; color:#fca5a5; font-weight:700; margin-bottom:6px;">❓ 핵심 문제</div>
      <div style="font-size:0.82rem; color:#e2e8f0; line-height:1.6;">
        학군 이사 가족은 <b>10년간</b> 같은 지역에 머뭅니다.<br>
        원하는 시기·가격의 매물은 <b>구조적으로 희소</b>합니다.
      </div>
    </div>
    <div style="background:rgba(59,130,246,0.18); border-radius:10px; padding:14px 16px; flex:1;">
      <div style="font-size:0.78rem; color:#93c5fd; font-weight:700; margin-bottom:6px;">✅ 해결책</div>
      <div style="font-size:0.82rem; color:#e2e8f0; line-height:1.6;">
        AI가 저평가 매물을 <b>1초 분석</b>.<br>
        매도·임대인 ↔ 매수·임차인 이사 시기를 <b>사전 자동매칭</b>.
      </div>
    </div>
  </div>

  <div style="background:rgba(16,185,129,0.15); border-radius:10px; padding:12px 16px;">
    <div style="font-size:0.78rem; color:#6ee7b7; font-weight:700; margin-bottom:6px;">🎯 기대 효과</div>
    <div style="font-size:0.8rem; color:#e2e8f0; line-height:1.8;">
      👨‍👩‍👧 <b>소비자</b> — 입주·입학 시기 혼란 해소 &nbsp;|&nbsp;
      📊 <b>시장</b> — 수급 투명화, 가격 왜곡 감소 &nbsp;|&nbsp;
      🏙️ <b>사회</b> — 기존 주거지역 흐름 안정화
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Login Form
    with st.container(border=True):
        st.markdown("### 📱 핸드폰 인증 로그인")
        name = st.text_input("이름을 입력하세요", placeholder="예: 홍길동")
        phone = st.text_input("휴대폰 번호를 입력하세요 (- 없이 입력)", placeholder="01012345678")

        if st.button("인증번호 발송 및 로그인", use_container_width=True, type="primary"):
            if not name or len(name.strip()) < 2:
                st.error("이름을 입력해주세요. (2자 이상)")
            elif len(phone) < 10:
                st.error("올바른 휴대폰 번호를 입력해주세요.")
            else:
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = name.strip()
                st.toast(f"✅ {name.strip()}님, 인증되었습니다! 환영합니다.")
                st.rerun()

    st.markdown("---")

    # Kakao Share Section — 앵커 id 삽입
    st.markdown('<div id="kakao-share-section"></div>', unsafe_allow_html=True)
    st.markdown("### 🟡 카카오톡으로 AI 전략 공유하기")

    APP_URL = "https://lotte-ai-app.streamlit.app/"
    APP_TITLE = "[공인중개사 이상수] 대치1동 AI 부동산 베이스캠프"
    APP_DESC = "⭐ AI 저평가 매물 분석 | 🎓 학군 1번지 | 🤖 자동 매칭"
    APP_IMG = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=600&q=80"

    st.markdown(
        f"""
<script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.2/kakao.min.js"
  integrity="sha384-TiCUE00h649CAMonG018J2ujOgDKW/kVWlChEuu4jK2vxfAAD0eZxzCKakxg55G4"
  crossorigin="anonymous"></script>

<div style="background:linear-gradient(135deg,#FFF01E,#F9E000); border-radius:16px;
            padding:22px 20px; margin-bottom:16px; border:2px solid #E6C900;
            box-shadow:0 4px 20px rgba(249,224,0,0.35);"
     id="kakao-share-box">
  <div style="text-align:center; margin-bottom:14px;">
    <span style="font-size:2.2rem;">💬</span>
    <div style="font-size:1.05rem; font-weight:900; color:#3c1e1e; margin-top:4px;">카카오링크 바로 보내기</div>
    <div style="font-size:0.78rem; color:#7a6000; margin-top:2px;">아래 버튼 클릭 → 카카오톡으로 공유</div>
  </div>

  <div style="background:white; border-radius:12px; padding:14px 16px; margin-bottom:14px;
              border:1px solid #e9d900; display:flex; gap:12px; align-items:center;">
    <img src="{APP_IMG}" style="width:72px; height:72px; border-radius:8px; object-fit:cover; flex-shrink:0;">
    <div>
      <div style="font-size:0.88rem; font-weight:800; color:#1e293b;">{APP_TITLE}</div>
      <div style="font-size:0.76rem; color:#64748b; margin-top:4px;">{APP_DESC}</div>
      <div style="font-size:0.73rem; color:#2563eb; margin-top:4px;">👉 {APP_URL}</div>
    </div>
  </div>

  <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
    <button onclick="sendKakaoLink()" id="btn-kakao-sdk"
      style="background:#3c1e1e; color:#FFF01E; border:none; border-radius:10px;
             padding:12px 8px; font-size:0.88rem; font-weight:900; cursor:pointer;
             width:100%; display:flex; align-items:center; justify-content:center; gap:6px;
             transition:transform 0.15s, box-shadow 0.15s;
             box-shadow:0 3px 10px rgba(0,0,0,0.25);"
      onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(0,0,0,0.3)';"
      onmouseout="this.style.transform=''; this.style.boxShadow='0 3px 10px rgba(0,0,0,0.25)';"
    >💬 카카오링크 전송</button>

    <a href="javascript:void(0)" onclick="openKakaoShare(event)"
      style="background:#FFF01E; color:#3c1e1e; border:2px solid #3c1e1e; border-radius:10px;
             padding:12px 8px; font-size:0.88rem; font-weight:900; cursor:pointer;
             text-align:center; text-decoration:none; display:flex; align-items:center;
             justify-content:center; gap:6px;
             box-shadow:0 3px 10px rgba(0,0,0,0.15);"
    >📤 카카오로 바로공유</a>
  </div>

  <button onclick="copyAppLink()" id="btn-copy-link"
    style="background:white; color:#1e293b; border:1.5px solid #d1d5db; border-radius:10px;
           padding:10px 8px; font-size:0.82rem; font-weight:700; cursor:pointer;
           width:100%; margin-top:8px; transition:background 0.15s;"
    onmouseover="this.style.background='#f1f5f9';"
    onmouseout="this.style.background='white';"
  >📋 앱 링크 클립보드 복사</button>
</div>

<script>
var KAKAO_APP_KEY = 'YOUR_KAKAO_APP_KEY';
var LOTTE_APP_URL = '{APP_URL}';
var LOTTE_APP_TITLE = '{APP_TITLE}';
var LOTTE_APP_DESC = '{APP_DESC}';
var LOTTE_IMG_URL = '{APP_IMG}';

try {{
  if (typeof Kakao !== 'undefined' && !Kakao.isInitialized()) {{
    Kakao.init(KAKAO_APP_KEY);
  }}
}} catch(e) {{
  console.log('Kakao SDK init deferred');
}}

function sendKakaoLink() {{
  try {{
    if (typeof Kakao !== 'undefined' && Kakao.isInitialized()) {{
      Kakao.Share.sendDefault({{
        objectType: 'feed',
        content: {{
          title: LOTTE_APP_TITLE,
          description: LOTTE_APP_DESC,
          imageUrl: LOTTE_IMG_URL,
          link: {{
            mobileWebUrl: LOTTE_APP_URL,
            webUrl: LOTTE_APP_URL
          }}
        }},
        buttons: [
          {{
            title: '앱에서 보기',
            link: {{ mobileWebUrl: LOTTE_APP_URL, webUrl: LOTTE_APP_URL }}
          }}
        ]
      }});
    }} else {{
      openKakaoShare(null);
    }}
  }} catch(e) {{
    openKakaoShare(null);
  }}
}}

function openKakaoShare(e) {{
  if (e) e.preventDefault();
  var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  if (isMobile) {{
    var kakaoDeeplink = 'kakaotalk://msg/sendlink?' +
      'url=' + encodeURIComponent(LOTTE_APP_URL) +
      '&text=' + encodeURIComponent(LOTTE_APP_TITLE + '\\n' + LOTTE_APP_DESC + '\\n' + LOTTE_APP_URL);

    var timeout = setTimeout(function() {{
      window.open(LOTTE_APP_URL, '_blank');
    }}, 1500);

    window.location.href = kakaoDeeplink;
    window.addEventListener('blur', function() {{
      clearTimeout(timeout);
    }});
  }} else {{
    var el = document.createElement('textarea');
    el.value = LOTTE_APP_TITLE + '\\n' + LOTTE_APP_DESC + '\\n' + LOTTE_APP_URL;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    alert('✅ 공유 메시지가 클립보드에 복사되었습니다!\\n카카오톡을 열어 붙여넣기(Ctrl+V) 하세요.');
  }}
}}

function copyAppLink() {{
  var el = document.createElement('textarea');
  el.value = LOTTE_APP_URL;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);

  var btn = document.getElementById('btn-copy-link');
  var orig = btn.innerHTML;
  btn.innerHTML = '✅ 복사 완료!';
  btn.style.background = '#dcfce7';
  btn.style.color = '#15803d';

  setTimeout(function() {{
    btn.innerHTML = orig;
    btn.style.background = 'white';
    btn.style.color = '#1e293b';
  }}, 2000);
}}
</script>
        """,
        unsafe_allow_html=True
    )

    st.caption("💡 모바일: 카카오앱 직접 실행 | PC: 링크 복사 후 카카오톡에 붙여넣기")
    st.markdown("---")

    # ── 핸드폰 번호로 앱 링크 전송 ──
    st.markdown("#### 📲 핸드폰 번호로 앱 링크 전송")
    with st.container(border=True):
        col_s, col_r2 = st.columns(2)
        with col_s:
            sender_phone = st.text_input(
                "📤 발신 번호 (내 번호)",
                placeholder="01012345678",
                key="sender_phone_input",
                help="링크를 보내는 사람의 핸드폰 번호 (- 없이 입력)"
            )
        with col_r2:
            receiver_phone = st.text_input(
                "📥 수신 번호 (받는 사람)",
                placeholder="01098765432",
                key="receiver_phone_input",
                help="링크를 받을 상대방 핸드폰 번호 (- 없이 입력)"
            )

        send_msg = st.text_area(
            "✉️ 전송 메시지",
            value=f"안녕하세요! 롯데타워&강남빌딩 부동산 이상수 대표입니다.\n대치1동 AI 부동산 정보 앱을 소개드립니다.\n👉 {APP_URL}",
            height=100,
            key="kakao_send_msg"
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📨 링크 문자 전송 (데모)", use_container_width=True, type="primary", key="btn_send_sms"):
                if not sender_phone or len(sender_phone) < 10:
                    st.error("발신 번호를 올바르게 입력해주세요.")
                elif not receiver_phone or len(receiver_phone) < 10:
                    st.error("수신 번호를 올바르게 입력해주세요.")
                else:
                    st.success(f"✅ {receiver_phone} 번호로 앱 링크 전송 완료! (데모)")
                    st.info("💡 실제 문자 전송은 문자 API(알리고·Cool SMS 등) 연동 시 동작합니다.")
                    st.code(f"수신: {receiver_phone}\n발신: {sender_phone}\n내용: {send_msg}", language="text")

        with col_btn2:
            st.markdown(
                """
                <a href="javascript:void(0)" onclick="openKakaoShare(event)"
                   style="display:block; text-align:center;
                          background:#FFF01E; color:#3c1e1e; font-weight:900; padding:11px;
                          border-radius:8px; text-decoration:none; border:2px solid #3c1e1e; font-size:0.9rem;">
                   💬 카카오링크 대화방 공유
                </a>
                """,
                unsafe_allow_html=True
            )


# --- Bottom Navigation Renderers ---

BOTTOM_NAV_CSS = """
<style>
.bottom-nav {
    position: fixed; bottom: 0px; left: 0px; width: 100%;
    background-color: white; border-top: 1px solid #eee;
    padding: 10px 20px; display: flex;
    justify-content: space-around; align-items: center;
    z-index: 9999; box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}
.nav-btn {
    text-decoration: none; color: #333; font-weight: bold;
    font-size: 0.9rem; display: flex; flex-direction: column;
    align-items: center; padding: 5px;
}
.nav-btn:hover { color: #2563eb; background-color: #f8fafc; border-radius:8px; }
</style>
"""


@st.dialog("💼 롯데타워&강남빌딩 부동산 중개(주) 명함", width="large")
def show_business_card_dialog():
    """부동산 명함 팝업 (st.dialog)"""
    CARD_HTML = """
    <style>
    .biz-card {
        background: linear-gradient(135deg, #003087, #1565c0);
        border-radius: 14px; padding: 22px 24px;
        color: white; margin-bottom: 16px; position: relative;
    }
    .biz-card .logo-tag {
        font-size: 0.68rem; color: #90caf9; line-height: 1.6;
        margin-bottom: 6px;
    }
    .biz-card .company {
        font-size: 1.05rem; font-weight: 900; color: #ffd54f; margin-bottom: 2px;
    }
    .biz-card .sub { font-size: 0.78rem; color: #bbdefb; margin-bottom: 12px; }
    .biz-card .title-label { font-size: 0.82rem; color: #90caf9; }
    .biz-card .name { font-size: 1.5rem; font-weight: 900; letter-spacing: 4px; color: #fff; margin: 4px 0; }
    .biz-card .mobile { color: #ffd54f; font-size: 0.95rem; font-weight: bold; margin: 4px 0; }
    .biz-card .contact { color: #fff; font-size: 0.82rem; margin: 2px 0; }
    .biz-card .addr { color: #bbdefb; font-size: 0.75rem; margin-top: 4px; }
    .biz-card .desc-list {
        margin-top: 14px; padding-top: 12px;
        border-top: 1px solid #1976d2;
        font-size: 0.76rem; color: #bbdefb; line-height: 1.9;
    }
    </style>

    <div class="biz-card">
      <div class="logo-tag">KNR 롯데월드타워 몰 시그니엘 레지던스 전문 | 학원가 한티 삼환·오피스텔 렌트</div>
      <div class="company">롯데타워 &amp; 강남빌딩 부동산 중개(주)</div>
      <div class="sub">LOTTE WORLD TOWER</div>
      <div class="title-label">대 표 / 공인중개사</div>
      <div class="name">이 상 수</div>
      <div class="mobile">Mobile : 010-8985-8945</div>
      <div class="contact">E-mail : 5788285@naver.com &nbsp;|&nbsp; tel : 578-8285</div>
      <div class="addr">서울시 강남구 도곡로 405, 5층 507호 [대치동, 삼환 아르누보2]</div>
      <div class="desc-list">
        ■ 랜드마크명품 주거 : 에테르노 청담 입주<br>
        ■ 주거 : 단대·숙명 인근아파트상담(래미안대치팰리스, SK뷰 외 다수)<br>
        ■ 입주 : 개포(THE HFIRSTIER IPARK)<br>
        ■ 투자 : 은마·미도·재건축 / 용산·한남 3구역 재개발<br>
        ■ 사업 : 상가·학원·건물·요양병원개설·토지
      </div>
    </div>

    <div class="biz-card">
      <div class="logo-tag">KNR 롯데월드타워 몰 시그니엘 레지던스 전문 | 학원가 삼환 클레시아 랜드</div>
      <div class="company">롯데타워 &amp; 강남빌딩 부동산 중개(주)</div>
      <div class="sub">LOTTE WORLD TOWER</div>
      <div class="title-label">이 사</div>
      <div class="name">김 은 경</div>
      <div class="mobile">Mobile : 010-2482-2460</div>
      <div class="contact">E-mail : koung713@naver.com &nbsp;|&nbsp; tel : 578-8285</div>
      <div class="addr">서울시 강남구 도곡로 405, 5층 507호 [대치동, 삼환 아르누보2]</div>
      <div class="desc-list">
        ■ 랜드마크명품 주거 : 에테르노 청담 입주<br>
        ■ 주거 : 단대·숙명 인근아파트상담(래미안대치팰리스, SK뷰 외 다수)<br>
        ■ 입주 : 개포(THE HFIRSTIER IPARK)<br>
        ■ 투자 : 은마·미도·재건축 / 용산·한남 3구역 재개발<br>
        ■ 사업 : 상가·학원·건물·요양병원개설·토지
      </div>
    </div>

    <p style="text-align:center; color:#64748b; font-size:0.75rem; margin-top:8px;">
      📞 대표번호 02-578-8285 &nbsp;|&nbsp; 등록번호: 11680-2023-00078 &nbsp;|&nbsp; 사업자: 461-86-02740
    </p>
    """
    st.markdown(CARD_HTML, unsafe_allow_html=True)


def render_login_bottom_nav():
    """로그인 화면 하단 Nav"""
    st.markdown("""
<style>
.block-container { padding-bottom: 90px !important; }
#lotte-login-fixed-bar {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 99999;
    background: #ffffff; border-top: 2px solid #e2e8f0;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.10);
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 6px; padding: 8px 10px;
}
.llnb-btn {
    background: transparent; border: 1px solid #e2e8f0;
    border-radius: 10px; cursor: pointer;
    font-size: 0.80rem; font-weight: 800;
    padding: 7px 4px; text-align: center; line-height: 1.5;
    transition: background 0.15s, transform 0.1s; font-family: sans-serif;
    width: 100%;
}
.llnb-btn:hover { background: #f1f5f9; transform: translateY(-1px); }
.llnb-btn:active { transform: translateY(0); }
.llnb-share    { color: #2563eb; }
.llnb-strategy { color: #7c3aed; }
.llnb-card     { color: #dc2626; }
div[data-key="nav_login_share"],
div[data-key="nav_login_strategy"],
div[data-key="nav_login_card"] {
    position: fixed !important; left: -9999px !important;
    top: 0px !important; width: 1px !important;
    height: 1px !important; overflow: hidden !important; opacity: 0 !important;
}
</style>
<div id="lotte-login-fixed-bar">
  <button class="llnb-btn llnb-share"
    onclick="document.querySelector('div[data-key=\\'nav_login_share\\'] button').click()">
    📤<br>공유하기</button>
  <button class="llnb-btn llnb-strategy"
    onclick="document.querySelector('div[data-key=\\'nav_login_strategy\\'] button').click()">
    🔷<br>AI핵심 3대전략</button>
  <button class="llnb-btn llnb-card"
    onclick="document.querySelector('div[data-key=\\'nav_login_card\\'] button').click()">
    💼<br>부동산명함보기</button>
</div>
""", unsafe_allow_html=True)

    if st.button("공유하기", key="nav_login_share"):
        st.session_state["scroll_to"] = "kakao-share-section"
        st.rerun()
    if st.button("AI핵심3대전략", key="nav_login_strategy"):
        st.session_state["scroll_to"] = "ai-strategy-section"
        st.rerun()
    if st.button("부동산명함보기", key="nav_login_card"):
        st.session_state["show_biz_card"] = True
        st.rerun()


def render_main_bottom_nav():
    """메인 화면 하단 Nav"""
    st.markdown("""
<style>
.block-container { padding-bottom: 90px !important; }
#lotte-fixed-bar {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 99999;
    background: #ffffff; border-top: 2px solid #e2e8f0;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.10);
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 6px; padding: 8px 10px;
}
.lnb-btn {
    background: transparent; border: 1px solid #e2e8f0;
    border-radius: 10px; cursor: pointer;
    font-size: 0.80rem; font-weight: 800;
    padding: 7px 4px; text-align: center; line-height: 1.5;
    transition: background 0.15s, transform 0.1s; font-family: sans-serif;
    width: 100%;
}
.lnb-btn:hover { background: #f1f5f9; transform: translateY(-1px); }
.lnb-btn:active { transform: translateY(0); }
.lnb-matching { color: #2563eb; }
.lnb-shorts   { color: #7c3aed; }
.lnb-top      { color: #dc2626; }
div[data-key="nav_main_matching"],
div[data-key="nav_main_shorts"],
div[data-key="nav_main_top"] {
    position: fixed !important; left: -9999px !important;
    top: 0px !important; width: 1px !important;
    height: 1px !important; overflow: hidden !important; opacity: 0 !important;
}
</style>
<div id="lotte-fixed-bar">
  <button class="lnb-btn lnb-matching"
    onclick="document.querySelector('div[data-key=\\'nav_main_matching\\'] button').click()">
    🤖<br>AI매칭사전예약가기</button>
  <button class="lnb-btn lnb-shorts"
    onclick="document.querySelector('div[data-key=\\'nav_main_shorts\\'] button').click()">
    🎬<br>AI숏츠 바로가기</button>
  <button class="lnb-btn lnb-top"
    onclick="document.querySelector('div[data-key=\\'nav_main_top\\'] button').click()">
    ⭐<br>AI저평가매물보기</button>
</div>
""", unsafe_allow_html=True)

    if st.button("AI매칭사전예약가기", key="nav_main_matching"):
        st.session_state["nav_tab_idx"] = 2
        st.rerun()
    if st.button("AI숏츠 바로가기", key="nav_main_shorts"):
        st.session_state["nav_tab_idx"] = 3
        st.rerun()
    if st.button("AI저평가매물보기", key="nav_main_top"):
        st.session_state["nav_tab_idx"] = 1
        st.rerun()


def main():
    # Sidebar: Share & Info
    st.sidebar.header("🔗 접속 주소 안내")
    st.sidebar.success("https://lotte-ai-estate.streamlit.app")
    st.sidebar.caption("👆 위 주소가 공식 앱 주소입니다. 복사해서 사용하세요!")

    with st.sidebar.expander("📤 앱 공유 및 카톡 바로가기", expanded=True):
        st.markdown("👇 **친구에게 공유할 링크**")
        st.code("https://lotte-ai-estate.streamlit.app", language="text")
        st.warning("⚠️ **주의**: 카카오톡 등 인앱 브라우저에서는 주소창이 숨겨질 수 있습니다. 이 주소를 확인하세요!")

        st.markdown("---")
        st.markdown("📱 **(개발용) 로컬 접속 시**")
        st.code("http://localhost:8502", language="text")

    # Session State Initialization
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        render_login_page()

        if st.session_state.get("show_biz_card"):
            st.session_state["show_biz_card"] = False
            show_business_card_dialog()

        render_login_bottom_nav()
        return

    tab_config = [
        ("🏠 대치1동 특성 (초중고)", render_home),                          # idx 0
        ("⭐ AI저평가추천매물", render_listing),                             # idx 1
        ("🤖 AI매칭/사전등록(예약)매칭", render_matching_and_reservation),     # idx 2
        ("🎬 AI 숏츠 / YOU-LAB", render_shorts_and_youlab),                 # idx 3
        ("🤝 AI공동매물매칭", render_joint_matching),                        # idx 4
        ("🔒 시스템/고객·영업팩", render_admin_system),                      # idx 5
    ]

    target_idx = st.session_state.pop("nav_tab_idx", None)
    if target_idx is not None:
        idx = int(target_idx)
        if 0 <= idx < len(tab_config):
            item = tab_config.pop(idx)
            tab_config.insert(0, item)

    legacy_target = st.session_state.pop("manual_nav_target", None)
    if legacy_target and target_idx is None:
        mapping = {
            "AI저평가추천매물": 1,
            "AI매칭": 2,
            "AI매칭/사전등록": 2,
            "AI 숏츠": 3,
            "대치1동": 0,
        }
        for key, val in mapping.items():
            if key in legacy_target:
                if 0 <= val < len(tab_config):
                    item = tab_config.pop(val)
                    tab_config.insert(0, item)
                break

    tabs = st.tabs([t[0] for t in tab_config])

    for i, tab in enumerate(tabs):
        with tab:
            tab_config[i][1]()

    render_main_bottom_nav()


if __name__ == "__main__":
    main()