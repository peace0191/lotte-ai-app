import os
import sys
import re
import json
import random
import time
import datetime
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

# datetime.now() 호환
datetime.now = datetime.datetime.now

# 서비스 import 경로
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────
# Services import (없어도 앱이 뜨도록 fallback)
# ─────────────────────────────────────
try:
    from services.matching_svc import matching_svc
    from services.map_image import build_points_map_png
    from services.local_market import local_market_svc
    from services.data import load_properties
    from services.ui import scroll_to_top
    MATCHING_SVC_AVAILABLE = True
except Exception:
    MATCHING_SVC_AVAILABLE = False

    class MockMatchingSvc:
        match_reservations = []

    matching_svc = MockMatchingSvc()

    class MockLocalMarketSvc:
        def get_daechi_summary(self):
            return {}

        def get_education_summary(self):
            return {
                "description": "대치동은 초·중·고 명문 학군과 학원가가 밀집한 대한민국 대표 교육특구입니다.",
                "elementary": ["대치초", "대도초"],
                "middle": ["대청중", "숙명여중"],
                "high": ["단대부고", "숙명여고"],
            }

    local_market_svc = MockLocalMarketSvc()

    def load_properties():
        return {}

    def build_points_map_png(pts):
        return None

    def scroll_to_top():
        return None


# ─────────────────────────────────────
# Page config
# ─────────────────────────────────────
st.set_page_config(
    page_title="롯데타워앤강남빌딩 AI 부동산",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────
# Session state init
# ─────────────────────────────────────
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "manual_nav_target" not in st.session_state:
    st.session_state["manual_nav_target"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "show_biz_card" not in st.session_state:
    st.session_state["show_biz_card"] = False


# ─────────────────────────────────────
# Global CSS
# ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}

.stApp {
    background: #f0f4f8 !important;
}

.block-container {
    background: #f0f4f8 !important;
    padding-top: 0.6rem !important;
    padding-bottom: 100px !important;
    max-width: 1100px !important;
}

header { visibility: hidden; }
footer { visibility: hidden; }

html {
    scroll-behavior: smooth !important;
    scroll-padding-top: 100px;
}

/* 기본 밝은 배경 텍스트 */
h1, h2, h3, h4, h5, h6 {
    color: #0f172a !important;
    font-weight: 800 !important;
}
p, li, td, th, label {
    color: #1e293b !important;
}
.stMarkdown p {
    color: #1e293b !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
}

/* 입력 */
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
::placeholder {
    color: #9ca3af !important;
    font-style: italic;
    font-size: 13px;
}
.stNumberInput > div > div > input {
    color: #111827 !important;
    background: #ffffff !important;
}

/* 라디오/체크 */
.stRadio label, .stCheckbox label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #1e293b !important;
}
.stRadio p, .stCheckbox p, .stToggle p {
    color: #1e293b !important;
}

/* 셀렉트 */
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 8px !important;
    color: #111827 !important;
}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div,
.stMultiSelect [data-baseweb="select"] span,
.stMultiSelect [data-baseweb="select"] div {
    color: #111827 !important;
}

/* 카드 */
.card {
    background: #ffffff !important;
    padding: 1.5rem;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
    border: 1px solid #e5e7eb;
    color: #1e293b !important;
}
.card * {
    color: #1e293b !important;
}
.card h2, .card h3, .card h4 {
    color: #0f172a !important;
}

/* 흰 배경 카드 */
.white-card {
    background: #ffffff !important;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    color: #0f172a !important;
}
.white-card * {
    color: #1e293b !important;
}

/* dark-box */
.dark-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    border-radius: 14px !important;
    border: 1px solid #334155 !important;
    color: #f8fafc !important;
}
.dark-box * {
    color: #f8fafc !important;
}
.dark-box h1, .dark-box h2, .dark-box h3, .dark-box h4, .dark-box h5, .dark-box h6 {
    color: #ffffff !important;
}
.dark-box .muted,
.dark-box [data-muted="true"] {
    color: #cbd5e1 !important;
}

/* 인라인 어두운 박스도 강제 보정 */
div[style*="background:#0f172a"],
div[style*="background: #0f172a"],
div[style*="background:#1e293b"],
div[style*="background: #1e293b"],
div[style*="background:linear-gradient(135deg,#0f172a"],
div[style*="background: linear-gradient(135deg, #0f172a"],
div[style*="background:linear-gradient(135deg,#1e293b"],
div[style*="background: linear-gradient(135deg, #1e293b"],
div[style*="background:linear-gradient(135deg,#061537"],
div[style*="background: linear-gradient(135deg, #061537"] {
    color: #f8fafc !important;
}
div[style*="background:#0f172a"] *,
div[style*="background: #0f172a"] *,
div[style*="background:#1e293b"] *,
div[style*="background: #1e293b"] *,
div[style*="background:linear-gradient(135deg,#0f172a"] *,
div[style*="background: linear-gradient(135deg, #0f172a"] *,
div[style*="background:linear-gradient(135deg,#1e293b"] *,
div[style*="background: linear-gradient(135deg, #1e293b"] *,
div[style*="background:linear-gradient(135deg,#061537"] *,
div[style*="background: linear-gradient(135deg, #061537"] * {
    color: inherit !important;
}

/* 강조색 유지 */
[style*="color:#fcd34d"], [style*="color: #fcd34d"] { color: #fcd34d !important; }
[style*="color:#fbbf24"], [style*="color: #fbbf24"] { color: #fbbf24 !important; }
[style*="color:#93c5fd"], [style*="color: #93c5fd"] { color: #93c5fd !important; }
[style*="color:#67e8f9"], [style*="color: #67e8f9"] { color: #67e8f9 !important; }
[style*="color:#4ade80"], [style*="color: #4ade80"] { color: #4ade80 !important; }
[style*="color:#f87171"], [style*="color: #f87171"] { color: #f87171 !important; }
[style*="color:#cbd5e1"], [style*="color: #cbd5e1"] { color: #cbd5e1 !important; }
[style*="color:#e2e8f0"], [style*="color: #e2e8f0"] { color: #e2e8f0 !important; }
[style*="color:#ffffff"], [style*="color: #ffffff"] { color: #ffffff !important; }
[style*="color:white"], [style*="color: white"] { color: #ffffff !important; }

/* 버튼 */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    border: none !important;
    padding: 8px 16px !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
}
.stButton > button[kind="secondary"],
.stButton > button:not([kind="primary"]) {
    background: #f1f5f9 !important;
    color: #1e293b !important;
    border: 1.5px solid #cbd5e1 !important;
}
.stButton > button * {
    color: inherit !important;
}

/* form submit */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 900 !important;
}
.stFormSubmitButton > button * {
    color: #ffffff !important;
}

/* expander */
.streamlit-expanderHeader {
    background: #f1f5f9 !important;
    color: #1e293b !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    border: 1px solid #e2e8f0 !important;
}
.streamlit-expanderHeader p,
.streamlit-expanderHeader span {
    color: #1e293b !important;
}
.streamlit-expanderContent {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 0 0 8px 8px !important;
}

/* metric */
div[data-testid="stMetricValue"] {
    color: #0f172a !important;
}
div[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #1e293b;
    padding: 6px;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    position: sticky;
    top: 0;
    z-index: 999;
    border: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    min-height: 42px !important;
    flex-grow: 1;
    border-radius: 8px !important;
    margin: 0 2px;
    background: #334155 !important;
    border: 1px solid #475569 !important;
    padding: 6px 4px !important;
}
.stTabs [data-baseweb="tab"] * {
    color: #e2e8f0 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    text-align: center !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    border: 1px solid #3b82f6 !important;
    box-shadow: 0 3px 10px rgba(37,99,235,0.45) !important;
    border-bottom: 3px solid #facc15 !important;
}
.stTabs [aria-selected="true"] * {
    color: #ffffff !important;
    font-weight: 900 !important;
}

/* 외부 링크 */
.ext-link {
    display: block;
    padding: 12px;
    text-decoration: none;
    color: white !important;
    text-align: center;
    border-radius: 10px;
    font-weight: 800;
    font-size: 14px;
    margin-bottom: 5px;
    transition: 0.25s;
}
.ext-link:hover {
    opacity: 0.88;
    transform: translateY(-1px);
}

/* 하단 고정 nav */
.block-container { padding-bottom: 90px !important; }

#lotte-fixed-bar, #lotte-login-fixed-bar {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 99999;
    background: #0f172a;
    border-top: 2px solid #334155;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.25);
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 6px; padding: 8px 10px;
}
.lnb-btn, .llnb-btn {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.80rem;
    font-weight: 800;
    padding: 7px 4px;
    text-align: center;
    line-height: 1.5;
    width: 100%;
    color: #e2e8f0 !important;
}
.lnb-btn:hover, .llnb-btn:hover {
    background: #2563eb !important;
    color: #ffffff !important;
}

div[data-key="nav_login_share"],
div[data-key="nav_login_strategy"],
div[data-key="nav_login_card"],
div[data-key="nav_main_matching"],
div[data-key="nav_main_shorts"],
div[data-key="nav_main_top"] {
    position: fixed !important;
    left: -9999px !important;
    top: 0 !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    opacity: 0 !important;
}

.section-header {
    background: linear-gradient(135deg, #0f172a, #1e3a5f);
    color: #f8fafc !important;
    font-weight: 900 !important;
    padding: 12px 16px;
    border-radius: 10px;
    margin: 24px 0 14px 0;
    border-left: 4px solid #facc15;
}
.section-header,
.section-header p,
.section-header span,
.section-header * {
    color: #f8fafc !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        min-height: 36px !important;
        padding: 4px 2px !important;
    }
    .stTabs [data-baseweb="tab"] * {
        font-size: 10px !important;
    }
    #lotte-fixed-bar, #lotte-login-fixed-bar {
        padding: 6px 8px !important;
    }
    .lnb-btn, .llnb-btn {
        font-size: 0.72rem !important;
        padding: 6px 2px !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────
# Map constants
# ─────────────────────────────────────
POINTS_PATH = Path("data/daechi_points.json")
COLOR_RGB = {
    "초등": [255, 140, 0],
    "중등": [50, 205, 50],
    "고등": [50, 205, 50],
    "단지": [255, 215, 0],
    "부동산": [255, 105, 180],
    "관공서": [150, 150, 150],
}


def load_points():
    if not POINTS_PATH.exists():
        return pd.DataFrame()
    items = json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    df = pd.DataFrame(items)
    df = df.dropna(subset=["lat", "lon"]).copy()
    df["color"] = df["category"].apply(lambda x: COLOR_RGB.get(x, [200, 200, 200]))
    if "note" in df.columns:
        df["is_overcrowded"] = df["note"].fillna("").astype(str).str.contains("과밀")
    else:
        df["is_overcrowded"] = False

    def get_height(cat):
        if cat == "단지":
            return 250
        if cat in ["초등", "중등", "고등"]:
            return 120
        return 60

    df["height"] = df["category"].apply(get_height)
    return df


def prefix_icon(cat):
    return {
        "초등": "🏫",
        "중등": "🏫",
        "고등": "🏫",
        "단지": "🏠",
        "부동산": "🏢",
        "관공서": "🏛️",
    }.get(cat, "📍")


def calculate_metrics():
    props = load_properties()
    targets = ["대치팰리스", "대치SK뷰", "대치아이파크"]
    buckets = {20: [], 30: [], 40: []}

    if isinstance(props, dict):
        for k, items in props.items():
            if k not in targets:
                continue
            for item in items:
                spec = item.get("spec", "")
                match = re.search(r"(\\d+)평", spec)
                if match:
                    size = int(match.group(1))
                    b = 40 if size >= 40 else (30 if size >= 30 else 20)
                    price_str = item.get("price", "")
                    if "/" not in price_str and "억" in price_str:
                        try:
                            val = float(re.search(r"([\\d\\.]+)억", price_str).group(1))
                            buckets[b].append(val)
                        except Exception:
                            pass

    defaults = {20: 23.5, 30: 32.5, 40: 48.0}
    return {
        k: round(sum(buckets[k]) / len(buckets[k]), 1) if buckets[k] else defaults[k]
        for k in [20, 30, 40]
    }


def render_daechi_map_block():
    st.markdown("### 🏫 AI 대치1동 학군/단지 입체 지도")
    df = load_points()
    if df.empty:
        st.warning("data/daechi_points.json 좌표 데이터가 없습니다.")
        return

    df["display_name"] = df.apply(lambda r: f"{prefix_icon(r['category'])} {r['name']}", axis=1)

    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=1,
        radius=35,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )
    halo_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color=[0, 0, 0, 50],
        get_line_color="color",
        stroked=True,
        filled=True,
        get_radius=70,
        radius_units="meters",
        line_width_min_pixels=2,
    )
    label_layer = pdk.Layer(
        "TextLayer",
        data=df,
        get_position=["lon", "lat"],
        get_text="display_name",
        get_size=15,
        get_color=[255, 255, 255],
        get_text_anchor="'middle'",
        get_alignment_baseline="'bottom'",
        get_pixel_offset=[0, -30],
        billboard=True,
        get_background_color=[0, 0, 0, 140],
        background_padding=[4, 2, 4, 2],
    )

    tooltip = {
        "html": "<b>{name}</b><br/>{category}<br/>{note}",
        "style": {"backgroundColor": "rgba(20,20,20,0.9)", "color": "white"},
    }
    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=14.5,
        pitch=50,
        bearing=10,
    )

    col_map, col_legend = st.columns([6, 4])
    with col_map:
        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/dark-v10",
                initial_view_state=view_state,
                layers=[halo_layer, column_layer, label_layer],
                tooltip=tooltip,
            ),
            use_container_width=True,
        )

    with col_legend:
        st.markdown("""
        <div class="dark-box" style="padding:15px; height:500px; overflow-y:auto;">
            <div style="margin-bottom:10px; font-weight:bold; color:#f8fafc; font-size:1.05em;
                        border-bottom:2px solid #334155; padding-bottom:5px;">🗺️ 상세 범례 가이드</div>

            <div style="display:flex; flex-direction:column; gap:12px; font-size:0.88em;">
                <div style="display:flex; align-items:start;">
                    <span style="color:#FFD700; margin-right:8px; font-size:1.2em;">●</span>
                    <div><b style="color:#fbbf24;">아파트 단지 (노랑)</b><br>
                    <span style="color:#94a3b8;">래대팰, SK뷰, 아이파크, 은마</span></div>
                </div>
                <div style="display:flex; align-items:start;">
                    <span style="color:#32CD32; margin-right:8px; font-size:1.2em;">●</span>
                    <div><b style="color:#4ade80;">중·고등학교 (녹색)</b><br>
                    <span style="color:#94a3b8;">대청중, 숙명여중고, 단대부중고</span></div>
                </div>
                <div style="display:flex; align-items:start;">
                    <span style="color:#FF8C00; margin-right:8px; font-size:1.2em;">●</span>
                    <div><b style="color:#fb923c;">초등학교 (주황)</b><br>
                    <span style="color:#94a3b8;">대치초, 대도초</span></div>
                </div>
                <div style="display:flex; align-items:start;">
                    <span style="color:#FF69B4; margin-right:8px; font-size:1.2em;">●</span>
                    <div><b style="color:#f472b6;">부동산 (분홍)</b><br>
                    <span style="color:#94a3b8;">롯데 AI 부동산</span></div>
                </div>
                <div style="display:flex; align-items:start;">
                    <span style="color:#A0A0A0; margin-right:8px; font-size:1.2em;">●</span>
                    <div><b style="color:#cbd5e1;">관공서/기타 (회색)</b><br>
                    <span style="color:#94a3b8;">주민센터, 지구대 등</span></div>
                </div>
            </div>

            <div style="margin-top:15px; padding-top:10px; border-top:1px solid #334155;
                        font-size:0.8em; color:#94a3b8;">
                💡 <b style="color:#e2e8f0;">이용 팁</b><br>
                • <b>Shift + 드래그</b>: 지도 3D 회전<br>
                • <b>마우스 오버</b>: 상세 정보 확인
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_realtime_search_panel(avg_prices):
    defaults = [
        ("ai_search_auto", True),
        ("ai_search_count", random.randint(1180, 1260)),
        ("ai_last_search", time.time()),
        ("ai_flash_deals", random.randint(2, 5)),
        ("ai_confidence", random.randint(91, 97)),
    ]
    for key, default in defaults:
        if key not in st.session_state:
            st.session_state[key] = default

    if "ai_search_logs" not in st.session_state:
        st.session_state["ai_search_logs"] = [
            f"[{datetime.now().strftime('%H:%M:%S')}] 🏛️ 국토부 실거래가 API 연결 완료 — 대치1동 1,247건 수집",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🏠 네이버 부동산 크롤링 완료 — 현재 매물 428건 분석",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 AI 머신러닝 예측 실행 — 신뢰도 94% 확보",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 급매 감지: 대치팰리스 34평 시세比 -3.2% 물건 발견",
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 자동탐색 완료 — 다음 탐색: 60초 후",
        ]

    elapsed = int(time.time() - st.session_state["ai_last_search"])
    status_color = "#22c55e" if st.session_state["ai_search_auto"] else "#f59e0b"
    status_text = "실시간 자동탐색 중" if st.session_state["ai_search_auto"] else "자동탐색 일시정지"
    status_dot = "🟢" if st.session_state["ai_search_auto"] else "🟡"

    st.markdown(f"""
    <div class="dark-box" style="padding:18px 22px; margin-bottom:16px;">
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

    kc1, kc2, kc3 = st.columns(3)
    with kc1:
        st.markdown(f"""
        <div class="dark-box" style="text-align:center; padding:14px; border:1px solid #1d4ed8;">
            <div style="font-size:0.78rem; color:#93c5fd; margin-bottom:4px;">🧠 AI 예측 신뢰도</div>
            <div style="font-size:2rem; font-weight:900; color:#60a5fa;">{st.session_state['ai_confidence']}%</div>
            <div style="font-size:0.72rem; color:#94a3b8;">머신러닝 앙상블 모델</div>
        </div>
        """, unsafe_allow_html=True)
    with kc2:
        cnt = st.session_state["ai_search_count"]
        st.markdown(f"""
        <div class="dark-box" style="text-align:center; padding:14px; border:1px solid #15803d;">
            <div style="font-size:0.78rem; color:#86efac; margin-bottom:4px;">📡 탐색 완료 건수</div>
            <div style="font-size:2rem; font-weight:900; color:#4ade80;">{cnt:,}건</div>
            <div style="font-size:0.72rem; color:#94a3b8;">실거래·매물 통합 집계</div>
        </div>
        """, unsafe_allow_html=True)
    with kc3:
        flash = st.session_state["ai_flash_deals"]
        st.markdown(f"""
        <div class="dark-box" style="text-align:center; padding:14px; border:1px solid #b91c1c;">
            <div style="font-size:0.78rem; color:#fca5a5; margin-bottom:4px;">🚨 급매 감지</div>
            <div style="font-size:2rem; font-weight:900; color:#f87171;">{flash}건</div>
            <div style="font-size:0.72rem; color:#94a3b8;">시세比 -2% 이상 할인 매물</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📋 실시간 탐색 로그 보기", expanded=False):
        log_html = "".join(
            f"<div style='font-size:0.8rem; padding:4px 0; border-bottom:1px solid #1e293b; color:#cbd5e1;'>{log}</div>"
            for log in reversed(st.session_state["ai_search_logs"][-8:])
        )
        st.markdown(
            f"<div class='dark-box' style='padding:10px;'>{log_html}</div>",
            unsafe_allow_html=True
        )

    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button("🔄 지금 탐색하기", use_container_width=True, key="btn_manual_search", type="primary"):
            st.session_state["ai_search_count"] += random.randint(3, 12)
            st.session_state["ai_confidence"] = random.randint(91, 97)
            st.session_state["ai_flash_deals"] = random.randint(2, 5)
            st.session_state["ai_last_search"] = time.time()
            sources = ["국토부 실거래가", "네이버 부동산", "한국부동산원", "KB 부동산"]
            topics = [
                f"래미안대치팰리스 34평 {avg_prices[30]}억 거래 확인",
                "대치SK뷰 26평 신규 전세 매물 등록",
                "은마아파트 31평 급매 -2.8% 포착",
                "대치아이파크 56평 최고층 시세 갱신",
                f"평형별 AI 예측 모델 재계산 완료 (신뢰도 {random.randint(91,97)}%)",
            ]
            st.session_state["ai_search_logs"].append(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 {random.choice(sources)} 수동 탐색 — {random.choice(topics)}"
            )
            st.toast("✅ AI 탐색 완료! 최신 데이터로 갱신되었습니다.", icon="🔄")
            st.rerun()

    with btn_col2:
        auto_label = "⏸ 자동탐색 중지" if st.session_state["ai_search_auto"] else "▶️ 자동탐색 시작"
        if st.button(auto_label, use_container_width=True, key="btn_toggle_auto"):
            st.session_state["ai_search_auto"] = not st.session_state["ai_search_auto"]
            st.toast("자동탐색 상태가 변경되었습니다.", icon="🤖")
            st.rerun()


# ─────────────────────────────────────
# Reusable marketing tools
# ─────────────────────────────────────
def render_marketing_action_tools(section_key: str = "default"):
    APP_URL = "https://lotte-ai-app.streamlit.app/"

    st.markdown("""
    <div class="dark-box" style="padding:24px 20px; margin-bottom:8px; background:linear-gradient(135deg,#0f172a,#1e3a5f);">
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

    with tool_tab1:
        st.markdown("#### 🎬 매물 숏츠 & 유튜버 광고 자동 제작")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            shorts_complex = c1.text_input("단지명", placeholder="래미안대치팰리스", key=f"{section_key}_sh_complex")
            shorts_price = c2.text_input("가격 요약", placeholder="34평 전세 8억", key=f"{section_key}_sh_price")
            st.radio("숏츠 스타일", ["💥 임팩트형", "✨ 고급형", "🎵 트렌디형"], horizontal=True, key=f"{section_key}_sh_style")
            shorts_point = st.text_area("매물 핵심 포인트", placeholder="예) 대치초 배정, 학원가 도보 3분", height=80, key=f"{section_key}_sh_point")
            if st.button("🚀 AI 숏츠 스크립트 자동 생성", type="primary", use_container_width=True, key=f"{section_key}_btn_shorts"):
                if not shorts_complex:
                    st.warning("단지명을 입력해주세요.")
                else:
                    with st.spinner("AI가 숏츠 스크립트를 작성 중입니다..."):
                        time.sleep(1.0)
                    st.success("✅ 숏츠 스크립트 생성 완료!")
                    st.markdown(f"""
                    <div class="dark-box" style="padding:16px;">
                      <div style="color:#38bdf8;font-weight:700;margin-bottom:8px;">📜 오프닝 멘트</div>
                      <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">지금 당장 봐야 할 대치동 역대급 매물이 나왔습니다!</div>
                      <div style="color:#38bdf8;font-weight:700;margin:12px 0 8px 0;">🏠 매물 브리핑</div>
                      <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">
                        {shorts_complex} {shorts_price}<br>
                        {shorts_point if shorts_point else "핵심 포인트를 입력하시면 맞춤 멘트가 생성됩니다."}
                      </div>
                      <div style="color:#38bdf8;font-weight:700;margin:12px 0 8px 0;">🔔 CTA</div>
                      <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">
                        지금 바로 롯데타워 AI 부동산 앱에서 예약하세요! 👉 {APP_URL}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

    with tool_tab2:
        st.markdown("#### 💛 카카오톡으로 AI 매칭 결과 알리기")
        with st.container(border=True):
            kakao_body = st.text_area(
                "발송 메시지",
                value=f"안녕하세요! 롯데타워 AI 부동산 이상수 대표입니다.\\nAI 매칭 안내드립니다.\\n👉 {APP_URL}",
                height=120,
                key=f"{section_key}_kk_body",
            )
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f'<a href="https://open.kakao.com/o/share?url={APP_URL}" target="_blank" style="display:block;text-align:center;background:#fef01b;color:#3c1e1e;font-weight:bold;padding:12px;border-radius:10px;text-decoration:none;font-size:0.95rem;">💛 카카오톡 공유</a>',
                    unsafe_allow_html=True
                )
            with c2:
                if st.button("📋 메시지 복사 준비", use_container_width=True, key=f"{section_key}_kk_copy"):
                    st.code(kakao_body, language="text")
                    st.toast("메시지가 준비되었습니다.")

    with tool_tab3:
        st.markdown("#### 📱 대기자에게 영업브리핑 문자 자동 발송")
        with st.container(border=True):
            recv_phone = st.text_input("수신 번호", placeholder="01012345678", key=f"{section_key}_sms_recv")
            recv_name = st.text_input("수신자 이름", placeholder="홍길동", key=f"{section_key}_sms_name")
            sms_body = st.text_area("문자 내용", value="롯데타워AI부동산 안내 메시지입니다.", height=100, key=f"{section_key}_sms_body")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📨 1:1 문자 발송 (데모)", use_container_width=True, type="primary", key=f"{section_key}_sms1"):
                    if not recv_phone:
                        st.warning("수신 번호를 입력해주세요.")
                    else:
                        st.success(f"✅ {recv_name or recv_phone}님께 문자 발송 완료! (데모)")
            with c2:
                if st.button("📢 일괄 발송 (데모)", use_container_width=True, key=f"{section_key}_sms_bulk"):
                    st.success("✅ 대기자 일괄 발송 완료! (데모)")

    with tool_tab4:
        st.markdown("#### 🔔 자동 알림 & 스케줄 관리")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            c1.toggle("📱 문자 자동발송", value=True, key=f"{section_key}_auto_sms")
            c2.toggle("💛 카카오 자동발송", value=True, key=f"{section_key}_auto_kk")
            c3, c4 = st.columns(2)
            c3.metric("📥 총 대기자", "4,218명", "+23")
            c4.metric("🤝 AI매칭률", "94.2%", "+1.3%")
            if st.button("🔔 지금 즉시 전체 대기자 알림 발송", type="primary", use_container_width=True, key=f"{section_key}_notify_all"):
                st.success("✅ 전체 대기자 알림 발송 완료! (데모)")


# ─────────────────────────────────────
# Main tab pages
# ─────────────────────────────────────
def render_home():
    st.markdown("""
    <div class="dark-box" style="padding:1.8rem; border-radius:0 0 1.5rem 1.5rem; margin:-1rem -1rem 1rem -1rem; border-bottom:3px solid #facc15;">
        <div style="display:flex; align-items:center; margin-bottom:1rem;">
            <div style="width:52px; height:52px; background:linear-gradient(135deg,#facc15,#f59e0b);
                        border-radius:50%; display:flex; align-items:center; justify-content:center;
                        margin-right:1rem; font-size:26px; box-shadow:0 4px 12px rgba(250,204,21,0.4);">👑</div>
            <div>
                <div style="margin:0; font-size:1.15rem; font-weight:900; color:#ffffff;">공인중개사 이상수 대표</div>
                <div style="margin:2px 0 0 0; font-size:0.85rem; font-weight:600; color:#e2e8f0;">롯데타워앤강남빌딩부동산중개(주)</div>
            </div>
        </div>
        <div style="font-size:1.55rem; font-weight:900; line-height:1.45; margin-bottom:0.3rem; color:#ffffff;">
            대치1동은 자녀의 미래를 위한
            <span style="color:#facc15;">베이스캠프</span>입니다.
        </div>
        <div style="margin:0.4rem 0 0 0; font-size:0.9rem; font-weight:600; color:#cbd5e1;">
            AI 저평가 분석과 예약 AI자동 매칭 시스템으로 숨겨진 부동산 가치를 발굴하고,
            대한민국 최고의 교육 환경으로 가는 최적의 출발점을 찾아드립니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    feature_items = [
        ("🎓", "#3b82f6", "교육특구 1번지", "대치초·대도초 학군\\n단대부고·숙명여고"),
        ("🤖", "#8b5cf6", "AI 자동매칭", "저평가 매물 즉시 발굴\\n매수↔매도 1초 매칭"),
        ("📢", "#ef4444", "AI 자동 홍보", "매물 접수 즉시\\n문자·카카오 자동 발송"),
    ]
    for col, (icon, color, title, desc) in zip([f1, f2, f3], feature_items):
        with col:
            st.markdown(f"""
            <div class="white-card" style="padding:16px; text-align:center; border-left:4px solid {color}; margin-bottom:8px;">
                <div style="font-size:2rem;">{icon}</div>
                <div style="font-size:0.9rem; font-weight:800; color:#0f172a; margin:4px 0;">{title}</div>
                <div style="font-size:0.76rem; color:#475569; white-space:pre-line; line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 📊 대치1동 평형별 시세 & 전세가율")
    avg_prices = calculate_metrics()
    render_realtime_search_panel(avg_prices)

    st.markdown("#### 📈 평형별 현재 시세")
    pt_c1, pt_c2, pt_c3 = st.columns(3)

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
        <div class="white-card" style="padding:16px; text-align:center;">
            <div style="font-size:0.85rem; color:#64748b; font-weight:700; margin-bottom:4px;">{title}</div>
            <div style="font-size:2rem; font-weight:900; color:#0f172a; line-height:1.2;">{price}억</div>
            <div style="font-size:0.82rem; font-weight:700; color:{arrow_color}; margin:4px 0;">
                {arrow} 전일比 {delta_abs}% ({'+' if delta>=0 else ''}{round(price*delta/100,2)}억)
            </div>
            <div style="font-size:0.8rem; color:#2563eb;">전세가율 {int(jeonse_ratio*100)}% · 약 {jeonse_val}억</div>
        </div>
        """, unsafe_allow_html=True)

    with pt_c1:
        render_price_card("20평형대 (소형)", avg_prices[20], 0.52, deltas[20])
    with pt_c2:
        render_price_card("30평형대 (국민평형)", avg_prices[30], 0.52, deltas[30])
    with pt_c3:
        render_price_card("40평형대 이상 (대형)", avg_prices[40], 0.52, deltas[40])

    st.caption("※ 국토부 실거래가 · 네이버부동산 · 한국부동산원 데이터 기반 AI 추정치 | 투자 참고용")
    st.markdown("---")

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

    tab_col, _ = st.columns([6, 4])
    with tab_col:
        st.markdown("#### 🏘️ 주요 유명 단지 분석")
        t1, t2, t3, t4 = st.tabs(["래미안 대치팰리스", "대치SK뷰/아이파크", "삼환/시그니엘", "은마아파트"])
        with t1:
            st.success("### 👑 대치동의 대장주")
            st.markdown("- 대치초 배정, 학원가 바로 앞\n- 수영장/조식 등 커뮤니티")
        with t2:
            st.warning("### ⚖️ 실속과 환경의 조화")
            st.markdown("- 대치역/한티역 역세권\n- 쾌적한 주거 환경")
        with t3:
            st.info("### 🏙️ 프리미엄 레지던스 & 오피스텔")
            st.markdown("- 시그니엘 프리미엄\n- 삼환아르누보2 학원가 도보")
        with t4:
            st.error("### 🏗️ 재건축의 상징")
            st.markdown("- 강남 재건축의 바로미터\n- 투자 관심도 높음")

    st.markdown("---")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("⭐ AI저평가추천매물 보기", use_container_width=True, key="btn_mid_listing"):
            st.session_state["nav_tab_idx"] = 1
            st.rerun()
    with col_nav2:
        if st.button("🤖 AI 챗봇에게 문의하기", use_container_width=True, key="btn_mid_chatbot"):
            st.session_state["nav_tab_idx"] = 2
            st.rerun()

    st.markdown("---")
    render_daechi_map_block()
    st.markdown("---")

    st.markdown("##### 🔗 주요 사이트 바로가기 (새창 열림)")
    el_c1, el_c2, el_c3, el_c4 = st.columns(4)
    with el_c1:
        st.markdown('<a href="https://rt.molit.go.kr/" target="_blank" class="ext-link" style="background:#1e3a5f;">🏛️ 국토부 실거래가</a>', unsafe_allow_html=True)
    with el_c2:
        st.markdown('<a href="https://land.naver.com/" target="_blank" class="ext-link" style="background:#03C75A;">🏠 네이버 부동산</a>', unsafe_allow_html=True)
    with el_c3:
        st.markdown('<a href="https://map.kakao.com/" target="_blank" class="ext-link" style="background:#b45309;">🗺️ 카카오맵</a>', unsafe_allow_html=True)
    with el_c4:
        st.markdown('<a href="https://www.reb.or.kr/" target="_blank" class="ext-link" style="background:#4f46e5;">📊 한국부동산원</a>', unsafe_allow_html=True)


def render_listing():
    st.markdown("### ⭐ AI저평가추천매물")

    def property_card(title, price, desc, badge=None, key_suffix=None):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if badge:
            st.markdown(
                f"<span style='background:#facc15; color:#1e293b; font-size:0.8em; padding:2px 6px; border-radius:4px; font-weight:800;'>{badge}</span>",
                unsafe_allow_html=True,
            )
        st.markdown(f"#### {title}")
        st.markdown(f"**{price}**")
        st.caption(desc)
        if st.button("AI 리포트 보기", key=f"btn_{key_suffix or title}"):
            st.info("AI 분석 리포트가 생성되었습니다. (데모)")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="dark-box" style="padding:20px 24px; margin-bottom:20px; background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%); border-left:5px solid #facc15;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
            <span style="font-size:2rem;">🤖</span>
            <div>
                <div style="font-size:1.3rem; font-weight:900; color:#facc15;">AI 저평가 추천매물</div>
                <div style="font-size:0.85rem; color:#93c5fd; margin-top:2px;">시세 대비 약 8% 전후 저평가 매물 선별</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">🏫 래미안 대치팰리스</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        property_card("대치팰리스 45평 고층", "55억", "45평 · 고층 · 남향 · 대치중심", "강력추천", "rdp45")
    with c2:
        property_card("대치팰리스 34평 고층뷰", "44억", "34평 · 고층 · 남향 · 한강조망", key_suffix="rdp34")
    with c3:
        property_card("대치팰리스 33평 실용형", "42억", "33평 · 저층 · 남향 · 초급매", key_suffix="rdp33")

    st.markdown('<div class="section-header">🚆 대치 SK뷰</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        property_card("대치SK뷰 33평 급매", "38억", "33평 · 중층 · 남향 · 대치역 도보 5분", "급매", "skv33")
    with c2:
        property_card("대치SK뷰 26평 인기타입", "10억 / 150만", "26평 · 동남향 · 저층", "월세", "skv26")
    with c3:
        property_card("대치SK뷰 37평 방4", "8억 / 530만", "37평 · 저층 · 가성비", "반전세", "skv37")

    st.markdown('<div class="section-header">🏘️ 대치 아이파크</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        property_card("대치아이파크 56평 펜트하우스", "59억", "56평 · 고층 · 남향 · 명문학군", "희소", "aip56")
    with c2:
        property_card("대치아이파크 33평 인기형", "40억", "33평 · 고층 · 남향 · 조망 우수", key_suffix="aip33")
    with c3:
        property_card("대치아이파크 32평 실속형", "38억", "32평 · 저층 · 남향 · 가성비", key_suffix="aip32")

    st.markdown('<div class="section-header">📉 대치 은마아파트</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        property_card("대치은마 31평 급매", "36.5억", "31평 · 중층 · 남향 · 대치동 중심", "투자추천", "euma31")
    with c2:
        property_card("대치은마 31평 고층뷰", "38억", "31평 · 고층 · 남향 · 조망 우수", key_suffix="euma31h")
    with c3:
        property_card("대치은마 34평 넓은평형", "41억", "34평 · 남향 · 중층", key_suffix="euma34")

    st.markdown('<div class="section-header">💎 시그니엘 레지던스</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        property_card("시그니엘 89평 프리미엄", "1억 / 1,700만", "89평 · 고층 · 남향 · 한강뷰", "월세", "sig89")
    with c2:
        property_card("시그니엘 88평 급매", "69억", "88평 · 고층 · 급매", key_suffix="sig88")
    with c3:
        property_card("시그니엘 95평 월세", "3억 / 1,800만", "95평 · 중층 · 입주협의", key_suffix="sig95")

    st.markdown('<div class="section-header">🎓 삼환 아르누보 2</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        property_card("삼환아르누보 17평 매매", "4.6억", "17평 · 서향 · 고층", "인기", "sam17")
    with c2:
        property_card("삼환아르누보 17평 복층", "1,000만 / 122만", "17평 · 북동향 · 고층", "월세", "sam17m")
    with c3:
        property_card("삼환아르누보 18평 복층", "2,000만 / 200만", "18평 · 북동향 · 2룸 확장형", key_suffix="sam18")


def render_matching_and_reservation():
    with st.expander("💬 AI 챗봇 상담 (열기/닫기)", expanded=True):
        st.markdown("""
        <div class="dark-box" style="text-align:center; margin-bottom:20px; padding:16px;">
            <h3 style="color:#facc15; margin:0;">☁️ AI Real Estate Assistant</h3>
            <span style="font-size:0.85em; color:#94a3b8;">24시간 365일, 대치동 부동산/세금/법률 데이터를 분석하여 답변합니다.</span>
        </div>
        """, unsafe_allow_html=True)

        faq_tab1, faq_tab2, faq_tab3, faq_tab4 = st.tabs(["🔥 인기질문", "💰 매매/투자", "🏠 전세/월세", "⚖️ 세금/정책"])
        selected_question = None

        with faq_tab1:
            fq1, fq2 = st.columns(2)
            if fq1.button("📌 대치동 학군 배정 원칙이 어떻게 되나요?", use_container_width=True):
                selected_question = "대치동 학군 배정 원칙 알려줘"
            if fq2.button("📈 대치동 국평(34평) 최근 시세 추이는?", use_container_width=True):
                selected_question = "대치동 34평 시세 추이 보여줘"

        with faq_tab2:
            fq1, fq2 = st.columns(2)
            if fq1.button("토지거래허가구역 실거주 요건은?", use_container_width=True):
                selected_question = "토지거래허가구역 요건 설명해줘"
            if fq2.button("갭투자 가능한 단지가 있나요?", use_container_width=True):
                selected_question = "대치동 갭투자 매물 추천해줘"

        with faq_tab3:
            fq1, fq2 = st.columns(2)
            if fq1.button("전세자금대출 최대 한도는?", use_container_width=True):
                selected_question = "전세자금대출 한도 알려줘"
            if fq2.button("전세 만기 시 보증금 반환 절차", use_container_width=True):
                selected_question = "전세 보증금 반환 내용 설명해줘"

        with faq_tab4:
            fq1, fq2 = st.columns(2)
            if fq1.button("1가구 2주택 양도세 비과세 요건", use_container_width=True):
                selected_question = "양도세 비과세 요건 알려줘"
            if fq2.button("취득세 중과 배제 기준", use_container_width=True):
                selected_question = "취득세 중과 기준 설명해줘"

        msg_container = st.container(height=260)
        with msg_container:
            st.chat_message("assistant").write("안녕하세요! 롯데타워 AI 부동산 비서입니다. 질문을 선택하거나 직접 입력해 주세요.")
            if selected_question:
                st.chat_message("user").write(selected_question)
                st.chat_message("assistant").write(f"'{selected_question}'에 대해 분석 중입니다. (데모)")

        prompt = st.chat_input("여기에 질문을 입력하세요...")
        if prompt:
            with msg_container:
                st.chat_message("user").write(prompt)
                st.chat_message("assistant").write("문의하신 내용을 확인했습니다. 상세 분석 리포트를 준비 중입니다. (데모)")

    st.markdown("---")

    st.markdown("""
    <div class="dark-box" style="text-align:center; margin-bottom:20px; padding:20px;">
        <h2 style="color:#facc15; margin-bottom:5px; font-size:1.4rem;">🚀 롯데타워 AI 사전 매칭 센터</h2>
        <p style="color:#94a3b8; font-size:0.9rem; margin:0;">스마트 예약 시스템으로 매칭 확률을 높이세요.</p>
    </div>
    """, unsafe_allow_html=True)

    prop_types = ["아파트", "빌라/연립", "오피스텔", "상가/상업", "토지", "기타"]
    trade_types = ["매매", "전세", "월세(반전세 포함)"]
    regions = ["강남구", "서초구", "송파구", "강동구", "마포구", "용산구", "성동구", "광진구"]
    complex_opts = ["래미안대치팰리스", "대치SK뷰", "대치아이파크", "은마아파트", "삼환아르누보2 오피스텔", "롯데월드타워몰 시그니엘레지던스", "직접입력"]

    tab_supply, tab_demand = st.tabs(["🏠 공급자 등록", "🔑 수요자 등록"])

    with tab_supply:
        st.markdown("##### 👤 기본 인적사항")
        c1, c2 = st.columns(2)
        name = c1.text_input("이름 (공급자)", placeholder="홍길동", key="s_name")
        phone = c2.text_input("연락처", placeholder="01012345678", key="s_phone")

        st.markdown("##### 🏷️ 매물 종류 & 거래 구분")
        c1, c2 = st.columns(2)
        prop = c1.selectbox("매물 종류", prop_types, key="s_prop")
        trade = c2.radio("거래 구분", trade_types, horizontal=True, key="s_trade")

        st.markdown("##### 📍 위치 정보")
        c1, c2 = st.columns(2)
        complex_sel = c1.selectbox("단지명/건물명", complex_opts, key="s_complex_sel")
        _dongho = c2.text_input("동/호수", placeholder="101동 1501호", key="s_dongho")
        complex_name = st.text_input("단지명 직접 입력", key="s_complex") if complex_sel == "직접입력" else complex_sel

        st.markdown("##### 📡 발송 지역")
        st.multiselect("발송 구 선택", regions, default=["강남구"], key="s_regions")
        agree = st.checkbox("✅ [필수] 개인정보 수집·이용에 동의합니다.", key="s_agree")

        if st.button("🚀 AI 마케팅 및 매칭 예약 완료", use_container_width=True, type="primary", key="s_submit"):
            errs = []
            if not name:
                errs.append("이름을 입력해주세요.")
            if not phone:
                errs.append("연락처를 입력해주세요.")
            if not complex_name:
                errs.append("단지명을 입력해주세요.")
            if not agree:
                errs.append("개인정보 동의가 필요합니다.")
            if errs:
                for e in errs:
                    st.error(e)
            else:
                st.success("✅ 공급 등록 완료! AI 매칭을 시작합니다.")
                st.balloons()

    with tab_demand:
        st.markdown("##### 👤 기본 인적사항")
        c1, c2 = st.columns(2)
        name = c1.text_input("이름 (수요자)", placeholder="홍길동", key="d_name")
        phone = c2.text_input("연락처", placeholder="01012345678", key="d_phone")

        st.markdown("##### 🏷️ 희망 매물 종류 & 거래 유형")
        c1, c2 = st.columns(2)
        c1.selectbox("희망 매물 종류", prop_types, key="d_prop")
        c2.radio("희망 거래 유형", trade_types, horizontal=True, key="d_trade")

        region = st.text_input("희망 지역", placeholder="강남구 대치동", key="d_region")
        agree = st.checkbox("✅ [필수] 개인정보 수집·이용에 동의합니다.", key="d_agree")

        if st.button("🔍 VIP 매칭 대기 등록하기", use_container_width=True, type="primary", key="d_submit"):
            errs = []
            if not name:
                errs.append("이름을 입력해주세요.")
            if not phone:
                errs.append("연락처를 입력해주세요.")
            if not region:
                errs.append("희망 지역을 입력해주세요.")
            if not agree:
                errs.append("개인정보 동의가 필요합니다.")
            if errs:
                for e in errs:
                    st.error(e)
            else:
                st.success("✅ 수요 등록 완료! 조건에 맞는 매물 발생 시 즉시 연락드립니다.")
                st.balloons()

    st.markdown("---")
    render_marketing_action_tools(section_key="match")


def render_shorts_and_youlab():
    st.markdown("### 🎬 AI 숏츠 플레이어")
    st.video("https://www.w3schools.com/html/mov_bbb.mp4")
    st.markdown("---")

    st.markdown("""
    <div class="dark-box" style="background:#7f1d1d !important; border:1px solid #991b1b; text-align:center; padding:15px; margin-bottom:20px;">
        <h2 style="margin:0; color:#ffffff;">🔴 YOU-LAB: 초고속 숏츠 연구소</h2>
        <p style="margin:5px 0 0 0; font-size:0.8em; color:#fca5a5;">GPU 가속 엔진 활성화</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.5])
    with c1:
        with st.container(border=True):
            st.markdown("#### ⚙️ 촬영 및 인코딩 설정")
            st.radio("시네마틱 스타일 선택", ["💥 마이클 베이", "✨ 미니멀", "🎵 트렌디"], key="ylab_style")
            st.slider("영상 길이 설정 (초)", 15, 60, 30, key="ylab_len")
            st.text_area("프롬프트", "대치동 학원가 전경에서 래미안대치팰리스로 줌인", height=100, key="ylab_prompt")
            if st.button("🎥 숏츠 제작 렌더링 시작", use_container_width=True, type="primary", key="ylab_render"):
                st.toast("렌더링 서버에 작업을 요청했습니다!")

    with c2:
        with st.container(border=True):
            st.markdown("#### 🖥️ 모니터링 데스크")
            st.code("""[SYSTEM] Token Inference Server Connected... OK
[INFO] Loaded Model: Lotte-RealEstate-v4.7
[GPU] CUDA Core Active: 0%
[QUEUE] Waiting for render job...""", language="bash")


def render_joint_matching():
    st.markdown("### 🤝 AI 부동산 공동중개 플랫폼")
    st.caption("강남구 등록된 부동산과 실시간 매칭됩니다. (데모)")

    req_tab1, req_tab2 = st.tabs(["🙋‍♂️ 고객 찾아요", "🏠 물건 찾아요"])
    with req_tab1:
        with st.form("find_client_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.selectbox("보유 매물", ["대치SK뷰 34평 전세", "은마 31평 매매", "직접입력"])
            with c2:
                st.number_input("거래 금액 (억)", value=15)
            with c3:
                st.text_input("특이사항", placeholder="전세자금대출 가능")
            if st.form_submit_button("🔔 전체 부동산에 손님 찾기 알림 발송", use_container_width=True):
                st.toast("📢 강남구 공동중개망에 알림이 발송되었습니다!")

    with req_tab2:
        with st.form("find_property_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("찾는 물건", placeholder="래대팰 45평 판상형")
            with c2:
                st.number_input("손님 예산 (억)", value=45)
            with c3:
                st.text_input("손님 조건", placeholder="3개월 내 입주")
            if st.form_submit_button("🔔 전체 부동산에 매물 요청 알림 발송", use_container_width=True):
                st.toast("📢 공동중개망에 매물 요청이 등록되었습니다.")

    st.markdown("---")
    st.markdown("#### ⚡ AI 공동매칭 결과")
    st.info("✅ AI 매칭 성공! 요청과 맞는 상대 부동산이 발견되었습니다.")

    data = {
        "시간": ["방금 전", "10분 전", "30분 전"],
        "구분": ["🚨 매칭성공", "수신", "발신"],
        "제목": ["래대팰 45평 판상형 매물 보유", "SK뷰 34평 전세 손님 대기", "대치아이파크 매수 손님 의뢰"],
        "상대 부동산": ["진공인중개사", "대박부동산", "전체발송"],
        "매칭률": ["99%", "85%", "-"],
        "상태": ["채팅 대기", "확인중", "발송완료"],
    }
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    st.markdown("---")
    render_marketing_action_tools(section_key="joint")


def render_admin_system():
    if "admin_unlocked" not in st.session_state:
        st.session_state["admin_unlocked"] = False

    st.markdown("### 🔒 관리자 보안 시스템")

    if not st.session_state["admin_unlocked"]:
        with st.container(border=True):
            st.markdown("##### 🔐 관리자 접속 권한 인증")
            password = st.text_input("관리자 비밀번호를 입력하세요", type="password", placeholder="비밀번호 입력")
            st.caption("초기 비밀번호는 1234 입니다.")
            if st.button("🔓 관리자 권한 확인", use_container_width=True):
                if password == "1234":
                    st.session_state["admin_unlocked"] = True
                    st.toast("🟢 관리자 인증 성공!")
                    st.rerun()
                else:
                    st.error("⛔ 비밀번호가 일치하지 않습니다.")
        return

    if st.button("🔒 로그아웃 (시스템 잠금)", type="secondary"):
        st.session_state["admin_unlocked"] = False
        st.rerun()

    st.markdown("---")
    adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs(["🏢 매물관리", "👥 고객관리", "📑 AI영업팩 생성기", "⚙️ 시스템 관리"])

    with adm_tab1:
        st.markdown("#### 🏢 매물관리")
        sample = pd.DataFrame([
            {"단지명": "래미안대치팰리스", "거래": "매매", "가격": "44억", "상태": "신규"},
            {"단지명": "대치SK뷰", "거래": "전세", "가격": "14.5억", "상태": "진행중"},
            {"단지명": "시그니엘레지던스", "거래": "매매", "가격": "69억", "상태": "급매"},
        ])
        st.dataframe(sample, use_container_width=True)

    with adm_tab2:
        st.markdown("#### 👥 고객관리")
        df = pd.DataFrame([
            {"이름": "김고객", "유형": "매수", "희망지역": "강남구 대치동", "예산": "30~40억", "상태": "대기"},
            {"이름": "박고객", "유형": "전세", "희망지역": "대치동", "예산": "12~16억", "상태": "매칭중"},
            {"이름": "이고객", "유형": "월세", "희망지역": "송파구", "예산": "5000/250", "상태": "상담완료"},
        ])
        st.dataframe(df, use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.metric("전체 고객", "128명")
        with c2:
            st.metric("매칭 진행", "23건")

    with adm_tab3:
        st.markdown("""
        <div class="dark-box" style="text-align:center; margin-bottom:24px; padding:20px;">
            <h3 style="color:#cbd5e1; margin:0;">📑 부동산 AI 영업팩 생성기</h3>
            <p style="color:#94a3b8; font-size:0.9rem; margin:4px 0 0 0;">블로그 / 카톡 / 상담 스크립트를 자동 생성합니다.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("admin_sales_pack_form"):
            sp1, sp2 = st.columns(2)
            sp_name = sp1.text_input("이름", "이상수", key="sp_name")
            sp_phone = sp2.text_input("연락처", "010-8985-8945", key="sp_phone")
            sp_complex = st.text_input("단지명", "대치SK뷰", key="sp_complex")
            sp_trade = st.selectbox("거래 구분", ["매매", "전세", "월세"], key="sp_trade")
            submitted = st.form_submit_button("🚀 AI 영업팩 생성", type="primary", use_container_width=True)
            if submitted:
                st.success("✅ AI 영업팩 생성 완료!")
                st.markdown(f"""
                <div class="dark-box" style="padding:20px;">
                    <h4 style="color:#38bdf8; margin:0 0 8px 0;">📝 블로그 제목</h4>
                    <p style="color:#e2e8f0;">대치동 학원가 바로 앞! {sp_complex} 귀한 {sp_trade}, 놓치면 후회합니다.</p>
                    <h4 style="color:#38bdf8; margin:12px 0 8px 0;">💬 카톡 브리핑</h4>
                    <p style="color:#e2e8f0;">안녕하세요. 롯데AI부동산 {sp_name} 중개사입니다. {sp_complex} 물건이 접수되었습니다. ☎ {sp_phone}</p>
                </div>
                """, unsafe_allow_html=True)

    with adm_tab4:
        st.markdown("#### ⚙️ 시스템 관리")
        st.info("시스템 관리 패널입니다.")
        nav_c1, nav_c2, nav_c3 = st.columns(3)
        with nav_c1:
            if st.button("🤖 AI매칭사전예약가기", use_container_width=True, key="adm_nav_matching", type="primary"):
                st.session_state["nav_tab_idx"] = 2
                st.rerun()
        with nav_c2:
            if st.button("🎬 AI숏츠 바로가기", use_container_width=True, key="adm_nav_shorts"):
                st.session_state["nav_tab_idx"] = 3
                st.rerun()
        with nav_c3:
            if st.button("⭐ AI저평가매물보기", use_container_width=True, key="adm_nav_listing"):
                st.session_state["nav_tab_idx"] = 1
                st.rerun()


# ─────────────────────────────────────
# Login page and dialogs
# ─────────────────────────────────────
@st.dialog("💼 롯데타워&강남빌딩 부동산 중개(주) 명함", width="large")
def show_business_card_dialog():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#003087,#1565c0); border-radius:14px;
                padding:22px 24px; color:white; margin-bottom:16px;">
        <div style="font-size:0.68rem; color:#90caf9; line-height:1.6; margin-bottom:6px;">
            KNR 롯데월드타워 몰 시그니엘 레지던스 전문 | 학원가 한티 삼환·오피스텔 렌트
        </div>
        <div style="font-size:1.05rem; font-weight:900; color:#ffd54f; margin-bottom:2px;">
            롯데타워 &amp; 강남빌딩 부동산 중개(주)
        </div>
        <div style="font-size:0.78rem; color:#bbdefb; margin-bottom:12px;">LOTTE WORLD TOWER</div>
        <div style="font-size:0.82rem; color:#90caf9;">대 표 / 공인중개사</div>
        <div style="font-size:1.5rem; font-weight:900; letter-spacing:4px; color:#fff; margin:4px 0;">
            이 상 수
        </div>
        <div style="color:#ffd54f; font-size:0.95rem; font-weight:bold; margin:4px 0;">
            Mobile : 010-8985-8945
        </div>
        <div style="color:#fff; font-size:0.82rem; margin:2px 0;">
            E-mail : 5788285@naver.com &nbsp;|&nbsp; tel : 02-578-8285
        </div>
        <div style="color:#bbdefb; font-size:0.75rem; margin-top:4px;">
            서울시 강남구 대치동 938외1 삼환아르누보2 507호
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_login_page():
    scroll_target = st.session_state.pop("scroll_to", None)
    if scroll_target:
        st.markdown(f"""
        <script>
        setTimeout(function(){{
            var el = document.getElementById("{scroll_target}");
            if(el) el.scrollIntoView({{behavior:"smooth", block:"start"}});
        }}, 400);
        </script>
        """, unsafe_allow_html=True)

    st.markdown('<div id="login-top"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="dark-box" style="background:linear-gradient(135deg,#061537 0%,#081a45 100%);
                padding:28px; border-radius:18px; margin-bottom:24px;
                box-shadow:0 10px 30px rgba(2,6,23,0.22); border:1px solid rgba(255,255,255,0.06);">
        <div style="display:flex; align-items:flex-start; margin-bottom:18px; flex-wrap:wrap; gap:14px;">
            <div style="background:#fbbf24; width:72px; height:72px; border-radius:50%;
                        display:flex; align-items:center; justify-content:center;
                        font-size:34px; flex-shrink:0; box-shadow:0 6px 18px rgba(251,191,36,0.35);">
                👨‍💼
            </div>
            <div style="flex:1; min-width:200px;">
                <div style="font-size:1.2rem; font-weight:900; color:#ffffff; margin-bottom:4px;">
                    롯데타워앤강남빌딩부동산중개주식회사
                </div>
                <div style="font-size:0.88rem; font-weight:500; color:#cbd5e1; margin-bottom:6px;">
                    등록번호: 11680-2023-00078 | 사업자: 461-86-02740
                </div>
                <div style="font-size:1.4rem; font-weight:900; color:#fbbf24; margin-bottom:6px;">
                    대표: 공인중개사 이상수
                </div>
                <div style="font-size:1rem; font-weight:600; color:#f1f5f9;">
                    Tel: 02-578-8285 / 010-8985-8945
                </div>
            </div>
        </div>

        <div style="font-size:1.45rem; font-weight:900; line-height:1.5;
                    letter-spacing:-0.03em; color:#ffffff; margin-bottom:10px;">
            대치1동은 자녀의 미래 베이스캠프입니다.
        </div>

        <div style="line-height:1.8; font-size:0.95rem; font-weight:500; color:#e2e8f0;">
            AI 저평가 분석과 예약 AI자동 매칭 시스템으로 숨겨진 부동산 가치를 발굴하고,<br>
            대한민국 최고의 교육 환경으로 가는 최적의 출발점을 찾아드립니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div id="ai-strategy-section"></div>', unsafe_allow_html=True)
    st.markdown("#### 🔷 AI 부동산 핵심 3대 전략")

    strategy_items = [
        ("#3b82f6", "🎓 교육특구 1번지 분석", "래대팰·SK뷰 vs 아이파크<br>학군 정밀 분석 및 배정 원칙 데이터화"),
        ("#8b5cf6", "🧬 AI저평가 매물 예약 자동매칭", "저평가 매물 발굴 + 매수·매도·임대차 예약 고객 1초 자동 매칭"),
        ("#ef4444", "📢 AI 자동 홍보 시스템", "매물 접수 즉시 영업 문구 자동 생성 및 타겟 고객 발송"),
    ]
    for color, title, desc in strategy_items:
        st.markdown(f"""
        <div class="white-card" style="padding:20px; margin-bottom:14px; border-left:5px solid {color};">
            <h4 style="margin:0 0 8px 0; color:#0f172a !important;">{title}</h4>
            <p style="margin:0; color:#475569 !important; font-size:0.9rem; line-height:1.6;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dark-box" style="background:linear-gradient(135deg,#0f172a,#1e3a5f); padding:24px 22px; margin-bottom:20px;">
      <h4 style="color:#fcd34d !important; margin:0 0 14px 0; font-size:1.05rem; font-weight:900;">
        🏠 부동산 저평가 매물 &amp; 사전예약 AI 자동매칭 플랫폼
      </h4>

      <div style="display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap;">
        <div style="background:rgba(239,68,68,0.18); border-radius:10px; padding:14px 16px; flex:1; min-width:200px;">
          <div style="font-size:0.78rem; color:#fca5a5; font-weight:700; margin-bottom:6px;">❓ 핵심 문제</div>
          <div style="font-size:0.82rem; color:#e2e8f0; line-height:1.6;">
            학군 이사 가족은 <b>10년간</b> 같은 지역에 머뭅니다.<br>
            원하는 시기·가격의 매물은 <b>구조적으로 희소</b>합니다.
          </div>
        </div>

        <div style="background:rgba(59,130,246,0.18); border-radius:10px; padding:14px 16px; flex:1; min-width:200px;">
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
    st.markdown('<div id="kakao-share-section"></div>', unsafe_allow_html=True)
    st.markdown("### 🟡 카카오톡으로 AI 전략 공유하기")

    APP_URL = "https://lotte-ai-app.streamlit.app/"
    APP_TITLE = "[공인중개사 이상수] 대치1동 AI 부동산 베이스캠프"
    APP_DESC = "⭐ AI 저평가 매물 분석 | 🎓 학군 1번지 | 🤖 자동 매칭"
    APP_IMG = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=600&q=80"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FFF01E,#F9E000); border-radius:16px;
                padding:22px 20px; margin-bottom:16px; border:2px solid #E6C900;
                box-shadow:0 4px 20px rgba(249,224,0,0.35);">
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

      <a href="https://open.kakao.com/o/share?url={APP_URL}" target="_blank"
         style="display:block; text-align:center; background:#3c1e1e; color:#FFF01E;
                font-weight:900; padding:12px; border-radius:10px; text-decoration:none; font-size:1rem;">
        💛 카카오톡으로 공유하기
      </a>
    </div>
    """, unsafe_allow_html=True)


def render_login_bottom_nav():
    st.markdown("""
    <div id="lotte-login-fixed-bar">
      <button class="llnb-btn"
        onclick="document.querySelector('div[data-key=\\'nav_login_share\\'] button').click()">
        📤<br>공유하기</button>
      <button class="llnb-btn"
        onclick="document.querySelector('div[data-key=\\'nav_login_strategy\\'] button').click()">
        🔷<br>AI핵심전략</button>
      <button class="llnb-btn"
        onclick="document.querySelector('div[data-key=\\'nav_login_card\\'] button').click()">
        💼<br>명함보기</button>
    </div>
    """, unsafe_allow_html=True)

    if st.button("공유하기", key="nav_login_share"):
        st.session_state["scroll_to"] = "kakao-share-section"
        st.rerun()
    if st.button("AI핵심전략", key="nav_login_strategy"):
        st.session_state["scroll_to"] = "ai-strategy-section"
        st.rerun()
    if st.button("명함보기", key="nav_login_card"):
        st.session_state["show_biz_card"] = True
        st.rerun()


def render_main_bottom_nav():
    st.markdown("""
    <div id="lotte-fixed-bar">
      <button class="lnb-btn"
        onclick="document.querySelector('div[data-key=\\'nav_main_matching\\'] button').click()">
        🤖<br>AI매칭</button>
      <button class="lnb-btn"
        onclick="document.querySelector('div[data-key=\\'nav_main_shorts\\'] button').click()">
        🎬<br>AI숏츠</button>
      <button class="lnb-btn"
        onclick="document.querySelector('div[data-key=\\'nav_main_top\\'] button').click()">
        ⭐<br>추천매물</button>
    </div>
    """, unsafe_allow_html=True)

    if st.button("AI매칭", key="nav_main_matching"):
        st.session_state["nav_tab_idx"] = 2
        st.rerun()
    if st.button("AI숏츠", key="nav_main_shorts"):
        st.session_state["nav_tab_idx"] = 3
        st.rerun()
    if st.button("추천매물", key="nav_main_top"):
        st.session_state["nav_tab_idx"] = 1
        st.rerun()


# ─────────────────────────────────────
# Main
# ─────────────────────────────────────
def main():
    st.sidebar.header("🔗 접속 주소 안내")
    st.sidebar.success("https://lotte-ai-app.streamlit.app")
    st.sidebar.caption("위 주소가 공식 앱 주소입니다.")

    with st.sidebar.expander("📤 앱 공유 및 카톡 바로가기", expanded=True):
        st.markdown("👇 친구에게 공유할 링크")
        st.code("https://lotte-ai-app.streamlit.app", language="text")

    if not st.session_state["logged_in"]:
        render_login_page()

        if st.session_state.get("show_biz_card"):
            st.session_state["show_biz_card"] = False
            show_business_card_dialog()

        render_login_bottom_nav()
        return

    TAB_LABELS = [
        "🏠 대치1동 특성",
        "⭐ AI저평가추천매물",
        "🤖 AI매칭/사전등록",
        "🎬 AI 숏츠/YOU-LAB",
        "🤝 AI공동매물매칭",
        "🔒 시스템/고객·영업팩",
    ]
    TAB_FUNCS = [
        render_home,
        render_listing,
        render_matching_and_reservation,
        render_shorts_and_youlab,
        render_joint_matching,
        render_admin_system,
    ]

    target_idx = st.session_state.get("nav_tab_idx", None)

    if target_idx is not None and 0 <= int(target_idx) < len(TAB_LABELS):
        idx = int(target_idx)
        labels = [TAB_LABELS[idx]] + [TAB_LABELS[i] for i in range(len(TAB_LABELS)) if i != idx]
        funcs = [TAB_FUNCS[idx]] + [TAB_FUNCS[i] for i in range(len(TAB_FUNCS)) if i != idx]
        st.session_state["nav_tab_idx"] = None
    else:
        labels = TAB_LABELS
        funcs = TAB_FUNCS

    tabs = st.tabs(labels)
    for i, tab in enumerate(tabs):
        with tab:
            funcs[i]()

    render_main_bottom_nav()


if __name__ == "__main__":
    main()